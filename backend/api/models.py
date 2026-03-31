from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    ROLE_CHOICES = [("Freelancer", "Freelancer"), ("Client", "Client")]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)
    profile_pic = models.ImageField(upload_to='profiles/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    reputation_points = models.IntegerField(default=0)

    #client related fields
    company_name = models.CharField(max_length=100, null=True, blank=True)
    project_type = models.CharField(max_length=100, null=True, blank=True)
    budget = models.IntegerField(null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    saved_freelancers = models.JSONField(default = list, blank=True, null=True)

    #freelancer related fields
    headline = models.CharField(max_length=100, blank=True, null=True)
    skills = models.JSONField(default = list, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    stipend = models.IntegerField(blank=True, null=True)
    bank_account = models.CharField(max_length=100, blank=True, null=True)
    
class PortfolioMedia(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='portfolio_media')
    media_type = models.CharField(max_length=10, choices=[('Image', 'Image'), ('Video', 'Video')])
    media_file = models.FileField(upload_to='portfolio_media/')
    
class Job(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Inprogress', 'InProhress'),
        ('Completed', 'Completed'),
        ('Closed', 'Closed')
    ]
    title = models.CharField(max_length=100)
    client = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='jobs_posted', null=True)
    description = models.TextField()
    skills = models.JSONField(default = list)
    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    stipend = models.IntegerField()

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Open')

    def __str__(self):
        return self.title
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending Payment', 'Pending Payment'),
        ('Confirmation Pending', 'Confirmation Pending'),
        ('Active', 'Active'),
        ('Work Submitted', 'Work Submitted'),
        ('Payment Rejected', 'Payment Rejected'),
        ('Completed', 'Completed'),
        ('Disputed', 'Disputed'),
    ]

    client = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='order_placed')
    freelancer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='order_received')
    project_name = models.CharField(max_length=255)
    requirements = models.TextField()
    deadline = models.DateField()
    amount = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending Payment')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_proof = models.ImageField(upload_to='payment_proof/', blank=True, null=True)
    admin_note = models.TextField(blank=True, null=True)
    
    # Dispute fields
    dispute_reason = models.TextField(null=True, blank=True)
    dispute_raised_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Work delivery (links only — no file storage)
    work_submission_text = models.TextField(null=True, blank=True)
    work_submission_link = models.URLField(max_length=500, null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.id

class Review(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    reviewer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='reviews_given')
    reviewee = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='reviews_received')
    
class OTP(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

class Conversation(models.Model):
    participants = models.ManyToManyField(Profile, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='messages_sent')
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

class Application(models.Model):
    STATUS_CHOICES = [('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected')]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    freelancer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='job_applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'freelancer')
        
    def __str__(self):
        return f"{self.freelancer.full_name} -> {self.job.title}"

    