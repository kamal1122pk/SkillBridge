from api.serializer import OrderSerializer
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializer import RegisterSerializer, OTPVerificationSerializer, ProfileSerializer, JobSerializer, PortfolioMediaSerializer, OrderSerializer, ReviewSerializer, ApplicationSerializer

# Create your views here.
def hello_world(request):
    return HttpResponse("Hello World")

@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "user created successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from .serializer import JobSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def postjob(request):
    serializer = JobSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(client=request.user.profile)
        return Response({"message": "Job posted"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def postportfolio(request):
    serializer = PortfolioMediaSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(profile=request.user.profile)
        return Response({"message": "Portfolio posted"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def postorder(request):
    serializer = OrderSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(client=request.user.profile)
        return Response({"message": "Order posted"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def updatepaymentproof(request, pk):
    try:
        # Ensure the user is the client who placed the order
        order = Order.objects.get(pk=pk, client=request.user.profile)
    except Order.DoesNotExist:
        return Response({"error": "Order not found or access denied"}, status=status.HTTP_404_NOT_FOUND)
    
    # partial=True allows sending only some fields (like just the image)
    serializer = PaymentProofSerializer(order, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save(status='Confirmation Pending')
        return Response({"message": "Payment proof uploaded successfully"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def confirmPayment(request, pk):
    try:
        order = Order.objects.get(pk=pk, freelancer=request.user.profile, status='Confirmation Pending')
    except Order.DoesNotExist:
        return Response({"error": "Order not found or access denied"}, status=status.HTTP_404_NOT_FOUND)
    
    order.status = 'Active'
    order.save()
    return Response({"message": "Payment confirmed"}, status=status.HTTP_200_OK)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def rejectPayment(request, pk):
    try:
        order = Order.objects.get(pk=pk, freelancer=request.user.profile, status='Confirmation Pending')
    except Order.DoesNotExist:
        return Response({"error": "Order not found or access denied"}, status=status.HTTP_404_NOT_FOUND)
    
    order.status = 'Payment Rejected'
    order.admin_note = request.data.get('admin_note')
    order.save()
    return Response({"message": "Payment rejected"}, status=status.HTTP_200_OK)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def submitWork(request, pk):
    try:
        order = Order.objects.get(pk=pk, freelancer=request.user.profile, status='Active')
    except Order.DoesNotExist:
        return Response({"error": "Order not found or access denied"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = OrderSerializer(order, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save(status='Work Submitted')
        return Response({"message": "Project submitted"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def acceptWork(request, pk):
    try:
        order = Order.objects.get(pk=pk, client=request.user.profile, status='Work Submitted')
    except Order.DoesNotExist:
        return Response({"error": "Order not found or access denied"}, status=status.HTTP_404_NOT_FOUND)
    
    order.status = 'Completed'
    order.save()
    return Response({"message": "Project accepted"}, status=status.HTTP_200_OK)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def rejectWork(request, pk):
    try:
        order = Order.objects.get(pk=pk, client=request.user.profile, status='Work Submitted')
    except Order.DoesNotExist:
        return Response({"error": "Order not found or access denied"}, status=status.HTTP_404_NOT_FOUND)

    order.status = 'Active'
    order.work_submission_text = None
    order.work_submission_file = None
    order.save()
    return Response({"message": "Client is not satisfied with the work. Please resubmit"}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def raiseDispute(request, pk):
    try:
        order = Order.objects.get(pk=pk, client=request.user.profile, status='Work Submitted')
    except Order.DoesNotExist:
        return Response({"error": "Order not found or access denied"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = OrderSerializer(order, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save(status='Disputed')
        return Response({"message": "Dispute raised successfully"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def resolveDispute(request, pk):
    if request.user.profile.role != 'Admin':
        return Response({"error": "Only admin can resolve disputes"}, status=status.HTTP_403_FORBIDDEN)
    try:
        order = Order.objects.get(pk=pk, status='Disputed')
    except Order.DoesNotExist:
        return Response({"error": "Order not found or access denied"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = OrderSerializer(order, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save(status='Completed')
        return Response({"message": "Dispute resolved successfully"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def postReview(request, pk):
    try:
        order = Order.objects.get(pk=pk, client=request.user.profile, status='Completed')
    except Order.DoesNotExist:
        return Response({"error": "Order not found or access denied"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ReviewSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(order=order, reviewer=request.user.profile, reviewee=order.freelancer)
        return Response({"message": "Review posted successfully"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def browserTalents(request):
    freelancers = Profile.objects.filter(role='Freelancer')
    serializer = ProfileSerializer(freelancers, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def browserJobs(request):
    jobs = Job.objects.filter(status='Open')
    serializer = JobSerializer(jobs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrders(request):
    orders = Order.objects.filter(client=request.user.profile)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def applyForJob(request, pk):
    try:
        job = Job.objects.get(pk=pk)
    except Job.DoesNotExist:
        return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ApplicationSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(job=job, freelancer=request.user.profile)
        return Response({"message": "Application submitted successfully"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getApplications(request):
    applications = Application.objects.filter(freelancer=request.user.profile)
    serializer = ApplicationSerializer(applications, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def acceptApplication(request, pk):
    try:
        application = Application.objects.get(pk=pk, job__client=request.user.profile)
    except Application.DoesNotExist:
        return Response({"error": "Application not found or access denied"}, status=status.HTTP_404_NOT_FOUND)
    
    application.status = 'Accepted'
    application.save()
    return Response({"message": "Application accepted"}, status=status.HTTP_200_OK)
    
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def rejectApplication(request, pk):
    try:
        application = Application.objects.get(pk=pk, job__client=request.user.profile)
    except Application.DoesNotExist:
        return Response({"error": "Application not found or access denied"}, status=status.HTTP_404_NOT_FOUND)
    
    application.status = 'Rejected'
    application.save()
    return Response({"message": "Application rejected"}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getProfile(request, pk):
    try:
        profile = Profile.objects.get(pk=pk)
    except Profile.DoesNotExist:
        return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ProfileSerializer(profile)
    return Response(serializer.data)