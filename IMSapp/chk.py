@login_required
def editpendingstudent(request, myid):
    studentdata = get_object_or_404(PendingStudentModel, id=myid)
    btcno = studentdata.BatchNo
    batchdata = get_object_or_404(BatchInfoModel, BatchNo=btcno)
    password = generate_random_password()
    
    initial_data = {
        'StudentName': studentdata.StudentName,
        'StudentPhoto': studentdata.StudentPhoto,
        'EducationalQualification': studentdata.EducationalQualification,
        'Religion': studentdata.Religion,
        'FatherName': studentdata.FatherName,
        'MotherName': studentdata.MotherName,
        'DOB': studentdata.DOB,
        'Gender': studentdata.Gender,
        'Mobile': studentdata.Mobile,
        'EmergencyContact': studentdata.EmergencyContact,
        'PresentAddress': studentdata.PresentAddress,
        'PermanentAddress': studentdata.PermanentAddress,
        'LearningBatch': batchdata,
    }
    

    if request.method == 'POST':
        studentform = StudentForm(request.POST, request.FILES, instance=studentdata)
        personalform = PersonalInfoForm(request.POST, instance=studentdata)
        courseenrollform = PendingEnrollCourseForm(request.POST, instance=studentdata)
        
        studentform.initial['StudentPhoto'] = initial_data['StudentPhoto']
        
        if studentform.is_valid() and personalform.is_valid() and courseenrollform.is_valid():
            student = studentform.save(commit=False)
            studentid = student.StudentID
            usertype = 'Student'
            
            student_exists = IMSUserModel.objects.filter(username=studentid).exists()
            
            if not student_exists:
                studentuser = IMSUserModel.objects.create_user(username=studentid, password=password, UserType=usertype)
                studentuser.save()
                student.Imsuser = studentuser
                student.save()
                
                personalinfo = personalform.save(commit=False)
                personalinfo.Imsuser = studentuser
                personalinfo.Password = password
                personalinfo.save()
                
                courseenroll = courseenrollform.save(commit=False)
                batchno = courseenroll.LearningBatch
                batch_exists = AdmittedCourseModel.objects.filter(Courseuser=studentuser, LearningBatch=batchno).exists()
                if not batch_exists:
                    batchdata = get_object_or_404(BatchInfoModel, BatchNo=batchno)
                    courseenroll.CourseName = batchdata.CourseName
                    courseenroll.Courseuser = studentuser
                    courseenroll.StudentID = studentid
                    coursefee = courseenroll.CourseFee
                    pay = courseenroll.Payment
                    courseenroll.Due = int(coursefee) - int(pay)
                    courseenroll.save()
                    
                    studentdata.delete()             
                    
                    messages.success(request, 'Successfully Added')
                    return redirect('pendingstudentlist')
                else:
                    messages.error(request, 'Batch Already Exists')
            else:
                messages.error(request, 'User Already Exists')
        else:
            messages.error(request, 'Form is not valid')
        
        # If the POST request didn't result in a redirect, re-render the form with errors
        context = {
            'studentform': studentform,
            'personalform': personalform,
            'courseenrollform': courseenrollform,
        }
        return render(request, 'students/editpendingstudent.html', context)
    
    else:
        studentform = StudentForm(initial=initial_data)
        personalform = PersonalInfoForm(initial=initial_data)
        courseenrollform = PendingEnrollCourseForm(initial=initial_data)
        context = {
            'studentform': studentform,
            'personalform': personalform,
            'courseenrollform': courseenrollform,
        }
        
        return render(request, 'students/editpendingstudent.html', context)