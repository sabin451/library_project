from .models import Book, Rental, Notification,Cart, CartItem,Category,UserProfile, Category, Rental, Purchase, PurchaseItem
from django.contrib.auth.models import User,auth
from django.contrib.auth import authenticate, login as auth_login
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from decimal import Decimal
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpResponse


def login(request):
    messages.warning(request,'please login')
    return redirect ('login_view')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('home')

def home(request):
    books = Book.objects.all()
    categories = Category.objects.all()
    context = {
        'books': books,
        'categories': categories,
        }
    return render(request, 'home.html', context)

def home_a(request):
    books = Book.objects.all()
    unapproved_users = UserProfile.objects.filter(is_approved=False).exclude(user__last_login__isnull=False)
    total_users_count = UserProfile.objects.all().count()
    total_unapproved_users = unapproved_users.count()
    total_rental_dues = get_user_rentals_next_day_count()
    context = {
        'books': books,
        'unapproved_users': unapproved_users,
        'total_users_count': total_users_count,
        'total_unapproved_users': total_unapproved_users,
        'total_rental_dues': total_rental_dues,
    }
    return render(request, 'home_a.html', context)

@login_required(login_url='login')
def home_u(request):
    current = request.user.id
    data = UserProfile.objects.get(user_id=current)
    books = Book.objects.all()
    categories = Category.objects.all()
    unapproved_users = UserProfile.objects.filter(is_approved=False).exclude(user__last_login__isnull=False)
    total_users_count = UserProfile.objects.all().count()
    now = datetime.now()
    end_of_day = now + timedelta(days=1)
    user_rentals_next_day = Rental.objects.filter(user=request.user,return_date__range=[now, end_of_day],returned_date__isnull=True);rental_count = user_rentals_next_day.count()
    cart_items_count = get_cart_items_count(request)
    context = {
        'data': data,
        'books': books,
        'categories': categories,
        'unapproved_users': unapproved_users,
        'total_users_count': total_users_count,
        'user_rentals_next_day': user_rentals_next_day,
        'rental_count': rental_count,
        'cart_items_count': cart_items_count,
        
    }    
    return render(request, 'home_u.html', context)

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff:
                auth_login(request, user)
                return redirect('home_a')
            try:
                user_profile = user.userprofile 
            except UserProfile.DoesNotExist:
                messages.error(request, 'User profile does not exist.')
                return redirect('login_view')
            if user_profile.is_approved:
                auth_login(request, user)
                messages.success(request, f'Welcome, {user.username}! You have successfully logged in.')
                return redirect('home_u')
            else:
                messages.warning(request, 'Your account is not yet approved. Please wait for approval.')
                return redirect('login_view')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login_view')
    return redirect('home')
import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile
from django.core.mail import send_mail

def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        contact_number = request.POST.get('contact_number')
        profile_picture = request.FILES.get('profile_picture')
        

        

        if not email.endswith('@gmail.com'):
            messages.error(request, 'Invalid email. Please use a valid email address.')
            return redirect('register')

        # Check if contact number is valid
        contact_number_pattern = re.compile(r'^\d{10}$')  # Regular expression for 10 digits
        if not contact_number_pattern.match(contact_number):
            messages.error(request, "Invalid contact number. Please enter a 10-digit number.")
            return redirect('register')

        # Check if contact number already exists
        if UserProfile.objects.filter(contact_number=contact_number).exists():
            messages.error(request, "Contact number is already registered.")
            return redirect('register')

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        # Check if username and email are unique
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already registered.")
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect('register')

        # Continue with user and profile creation
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        profile = UserProfile(
            user=user,
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            contact_number=contact_number,
            profile_picture=profile_picture
        )
        profile.save()

        # Send registration confirmation email
        send_mail(
            'Registration Confirmation',
            f'Hey {first_name} {last_name}, Your registration is complete. Thank you for registering!\n\nUsername: {username}\nPassword: {password}',
            'your@email.com',
            [email],
            fail_silently=False,
        )

        messages.success(request, "Registration successful. Check your email for the confirmation.")
        return redirect('home')

    return render(request, 'register.html')



@login_required(login_url='login')
def admin_dashboard(request):
    users_to_approve = UserProfile.objects.all()
    total_rental_dues = get_user_rentals_next_day_count()
    total_unapproved_users = get_unapproved_users_count()
    context={
        'users_to_approve': users_to_approve,
        'total_rental_dues': total_rental_dues,
        'total_unapproved_users': total_unapproved_users,       
    }
    return render(request, 'admin_dashboard.html', context)

@login_required(login_url='login')
def approve_user(request, user_id):
    user_profile = get_object_or_404(UserProfile, pk=user_id)
    user_profile.is_approved = True
    user_profile.save()
    return redirect('admin_dashboard')

@login_required(login_url='login')
def disapprove_user(request, user_id):
    user_profile = get_object_or_404(UserProfile, pk=user_id)
    user_profile.is_approved = False
    user_profile.save()
    return redirect('admin_dashboard')

@login_required(login_url='login')
def book_management(request):
    unapproved_users = UserProfile.objects.filter(is_approved=False).exclude(user__last_login__isnull=False)
    total_users_count = UserProfile.objects.all().count()
    total_rental_dues = get_user_rentals_next_day_count()
    total_unapproved_users = get_unapproved_users_count()
    books = Book.objects.all()
    context = {
        'unapproved_users': unapproved_users,
        'total_users_count': total_users_count,
        'books': books,
        'total_unapproved_users':total_unapproved_users,
        'total_rental_dues' : total_rental_dues,       
    }
    return render(request, 'book_management.html',context)

@login_required(login_url='login')
def book_management_u(request):
    data = UserProfile.objects.get(user=request.user)
    categories = Category.objects.prefetch_related(Prefetch('book_set', queryset=Book.objects.all())).all()
    now = datetime.now()
    end_of_day = now + timedelta(days=1)
    user_rentals_next_day = Rental.objects.filter(user=request.user,return_date__range=[now, end_of_day],returned_date__isnull=True)
    rental_count = user_rentals_next_day.count()
    cart_items_count = get_cart_items_count(request)
    context = {
        'categories': categories,
        'data': data,
        'user_rentals_next_day': user_rentals_next_day,
        'rental_count': rental_count,
        'cart_items_count': cart_items_count,
        
    }
    return render(request, 'book_management_u.html', context)

def add_category(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        if Category.objects.filter(name=category_name).exists():
            messages.error(request, "Already Exists")
        else:
            new_category = Category(name=category_name)
            new_category.save()
            messages.success(request, "Category added")
        return redirect('add_category')
    total_rental_dues = get_user_rentals_next_day_count()
    total_unapproved_users = get_unapproved_users_count()
    context={
        'total_rental_dues' : total_rental_dues,
        'total_unapproved_users':total_unapproved_users,
    }
    return render(request, 'add_category.html',context)

def categories(request):
    categories = Category.objects.all()
    total_rental_dues = get_user_rentals_next_day_count()
    total_unapproved_users = get_unapproved_users_count()
    context={
        'categories' : categories,
        'total_rental_dues' : total_rental_dues,
        'total_unapproved_users' : total_unapproved_users,
    }
    return render(request, 'categories.html',context)

def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        new_name = request.POST.get('new_name')
        if new_name:
            category.name = new_name
            category.save()
            return redirect('categories')
        else:
            return HttpResponse("Invalid data submitted.")
    total_rental_dues = get_user_rentals_next_day_count()
    total_unapproved_users = get_unapproved_users_count()
    context={
        'category' : category,
        'total_rental_dues' : total_rental_dues,
        'total_unapproved_users' : total_unapproved_users,
    }
    return render(request, 'edit_category.html', context)

def delete_category(request,category_id):
    category=Category.objects.get(id=category_id)
    category.delete()
    return redirect('categories')

@login_required(login_url='login')
def add_book(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        author = request.POST.get('author')
        publisher = request.POST.get('publisher')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        category_id = request.POST.get('category')
        image = request.FILES.get('image') 
        if not all([name, author, publisher, price, stock, category_id, image]):
            messages.error(request, 'Please fill in all the fields.')
            return redirect('add_book')
        if not price.isdigit() or not stock.isdigit():
            messages.error(request, 'Price and stock must be numeric values.')
            return redirect('add_book')
        if len(name) < 3:
            messages.error(request, 'Name must be at least 3 characters long.')
            return redirect('add_book')
        if Book.objects.filter(name=name).exists():
            messages.error(request, 'A book with the same name already exists.')
            return redirect('add_book')
        new_book = Book(name=name,author=author,publisher=publisher,price=price,stock=stock,image=image)
        new_book.save()
        if category_id:
            category = Category.objects.get(pk=category_id)
            new_book.categories.add(category)
            messages.success(request, 'Book added successfully.')
            return redirect('add_book')
    categories = Category.objects.all()    
    total_rental_dues = get_user_rentals_next_day_count()
    total_unapproved_users = get_unapproved_users_count()    
    context={
        'categories': categories,
        'total_rental_dues' : total_rental_dues,
        'total_unapproved_users' : total_unapproved_users,
    }
    return render(request, 'add_book.html', context)

@login_required(login_url='login')
def edit_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    categories = Category.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        author = request.POST.get('author')
        publisher = request.POST.get('publisher')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        category_id = request.POST.get('category')  
        image = request.FILES.get('image')
        book.name = name
        book.author = author
        book.publisher = publisher
        book.price = price
        book.stock = stock
        if image:
            file_name = f'book_images/{name}_{book_id}_{image.name}'
            file_path = default_storage.save(file_name, ContentFile(image.read()))
            book.image.name = file_path
        book.categories.clear() 
        if category_id:
            category = Category.objects.get(pk=category_id)
            book.categories.add(category)
        book.save()
        return redirect('book_management')
    total_rental_dues = get_user_rentals_next_day_count()
    total_unapproved_users = get_unapproved_users_count()
    context={
        'book': book,
        'categories': categories,
        'total_rental_dues' : total_rental_dues,
        'total_unapproved_users' : total_unapproved_users,
    }
    return render(request, 'edit_book.html', context)

@login_required(login_url='login')
def delete_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    book.delete()
    return redirect('book_management')

@login_required(login_url='login')
def view_users(request):
    users = UserProfile.objects.all()
    total_rental_dues = get_user_rentals_next_day_count()
    total_unapproved_users = get_unapproved_users_count()
    context={
        'users': users,
        'total_rental_dues': total_rental_dues,
        'total_unapproved_users': total_unapproved_users,
    }
    return render(request, 'view_users.html', context)

@login_required(login_url='login')
def search_books(request):
    books = []
    if 'query' in request.GET:
        query = request.GET['query']
        books = Book.objects.filter(name__icontains=query) | Book.objects.filter(author__icontains=query)
    data = UserProfile.objects.get(user=request.user)
    now = datetime.now()
    end_of_day = now + timedelta(days=1)
    user_rentals_next_day = Rental.objects.filter(user=request.user,return_date__range=[now, end_of_day],returned_date__isnull=True);rental_count = user_rentals_next_day.count() 
    cart_items_count = get_cart_items_count(request)
    context={
        'books': books,
        'data':data,
        'user_rentals_next_day': user_rentals_next_day,
        'rental_count': rental_count,
        'cart_items_count': cart_items_count,
    }
    return render(request, 'search_books.html', context)

@login_required(login_url='login')
def user_requests(request):
    context = {
    }  
    return render(request, 'user_requests.html', context)


@login_required(login_url='login')
def report_lost_book(request, rental_id):
    rental = get_object_or_404(Rental, pk=rental_id)
    if request.method == 'POST':
        if not rental.is_lost:
            rental.is_lost = True
            rental.fine_amount =float(rental.fine_amount)+ float(rental.book.price) + (0.5 * float(rental.book.price))
            rental.save()
            rental.book.save()
            messages.success(request, 'Lost book reported successfully. Fine amount: ${:.2f}'.format(rental.fine_amount))
            return redirect('rental_history')
        else:
            messages.error(request, 'This book has already been reported as lost.')
            return redirect('rental_history')
    return render(request, 'report_lost_book.html', {'rental': rental})






@login_required(login_url='login')
def overdue_inform(request, rental_id):
    rental = get_object_or_404(Rental, pk=rental_id)
    if rental.return_date and timezone.is_aware(rental.return_date):
        return_date_aware = rental.return_date
    elif rental.return_date:
        return_date_aware = timezone.make_aware(rental.return_date)
    else:
        return_date_aware = None
    if return_date_aware and return_date_aware < timezone.now():
        overdue_days = (timezone.now() - return_date_aware).days
        fine_amount = overdue_days * 5
        rental.fine_amount = fine_amount
        rental.save()
    messages.success(request, 'Overdue inform successful.')
    total_rental_dues = get_user_rentals_next_day_count()
    total_unapproved_users = get_unapproved_users_count()
    context={
        'rental': rental,
        "total_rental_dues": total_rental_dues,
        "total_unapproved_users" : total_unapproved_users
    }
    return render(request, 'overdue_inform.html', context)

@login_required(login_url='login')
def purchase_books(request):
    if request.method == 'POST':
        book_ids = request.POST.getlist('book_id')
        quantities = request.POST.getlist('quantity')
        quantities = [int(q) for q in quantities]
        books = Book.objects.filter(pk__in=book_ids)
        total_amount = 0
        for book, quantity in zip(books, quantities):
            if book.stock < quantity:
                messages.error(request, f"Insufficient stock for {book.name}.")
                return redirect('browse_books')
            total_amount += book.price * quantity
        with transaction.atomic():
            user = request.user
            purchase = Purchase.objects.create(user=user, total_amount=total_amount)
            for book, quantity in zip(books, quantities):
                purchase.books.add(book, through_defaults={'quantity': quantity})
            for book, quantity in zip(books, quantities):
                book.stock -= quantity
                book.save()
            send_purchase_confirmation_email(user, purchase)
        messages.success(request, f"Purchase successful. Total amount: ${total_amount:.2f}")
        return redirect('purchase_history')
    else:
        books = Book.objects.filter(stock__gt=0)
        cart_items_count = get_cart_items_count(request)
        context={
            'books': books,
            'cart_items_count': cart_items_count
            }
        return render(request, 'purchase_books.html', context)
    
@login_required(login_url='login')
def send_purchase_confirmation_email(user, purchase):
    subject = 'Purchase Confirmation'
    from_email = 'your@email.com' 
    to_email = user.email  
    message = render_to_string('purchase_confirmation_email.txt', {'purchase': purchase})
    plain_message = strip_tags(message)
    send_mail(subject, plain_message, from_email, [to_email], html_message=message, fail_silently=False)

import re
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import UserProfile, Rental
from datetime import datetime, timedelta

@login_required(login_url='login')
def reset_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')

        # Password validation criteria
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$', new_password):
            messages.error(
                request, 'Password must contain at least 1 lowercase letter, 1 uppercase letter, 1 digit, 1 special character, and be at least 6 characters long.'
            )
            return redirect('reset_password')

        try:
            user = User.objects.get(username=username, email=email)
            user.password = make_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            subject = 'Password Reset Successful'
            message = f'Your password has been successfully reset.\n username:{username}\n New password: {new_password}'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]
            send_mail(subject, message, from_email, recipient_list)
            messages.success(request, 'Password reset successfully. You can now log in with your new password.')
            return redirect('home')
        except User.DoesNotExist:
            messages.error(request, 'Invalid username or email. Please check your credentials.')
            return redirect('reset_password')

    data = UserProfile.objects.get(user=request.user)
    now = datetime.now()
    end_of_day = now + timedelta(days=1)
    user_rentals_next_day = Rental.objects.filter(
        user=request.user,
        return_date__range=[now, end_of_day],
        returned_date__isnull=True
    )
    rental_count = user_rentals_next_day.count()
    cart_items_count = get_cart_items_count(request)
    context = {
        "data": data,
        'cart_items_count': cart_items_count,
        'rental_count': rental_count,
    }

    return render(request, 'reset_password.html', context)

def view_profile(request):
    data=UserProfile.objects.get(user_id=request.user.id)
    
    now = datetime.now()
    end_of_day = now + timedelta(days=1)
    user_rentals_next_day = Rental.objects.filter(user=request.user,return_date__range=[now, end_of_day],returned_date__isnull=True);rental_count = user_rentals_next_day.count()
    cart_items_count = get_cart_items_count(request)
    context={
        'data':data,
        'user_rentals_next_day': user_rentals_next_day,
        'rental_count': rental_count,
        'cart_items_count': cart_items_count,
    }
    return render(request,'view_profile.html',context)



@login_required(login_url='login')
def edit_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    user = request.user 

    if request.method == 'POST':
        # Validate email
        email = request.POST['email']

        if '@' not in email:
            messages.error(request, 'Invalid email. Please include "@" in your email.')
            return redirect('edit_profile')

        if not email.endswith('@gmail.com'):
            messages.error(request, 'Invalid email domain. Please use a valid email address.')
            return redirect('edit_profile')

        contact_number = request.POST['contact_number']
        if not contact_number.isdigit() or len(contact_number) != 10:
            messages.error(request, 'Invalid contact number. It should be a 10-digit number.')
            return redirect('edit_profile')
        if UserProfile.objects.filter(email=email).exclude(user=user).exists():
            messages.error(request, 'Email is already in use by another user.')
            return redirect('edit_profile')

        if UserProfile.objects.filter(contact_number=contact_number).exclude(user=user).exists():
            messages.error(request, 'Contact number is already in use by another user.')
            return redirect('edit_profile')
        username = request.POST['username']
        if User.objects.filter(username=username).exclude(id=user.id).exists():
            messages.error(request, 'Username is already in use by another user.')
            return redirect('edit_profile')
        user_profile.username = username
        user_profile.email = email
        user_profile.first_name = request.POST['first_name']
        user_profile.last_name = request.POST['last_name']
        user_profile.contact_number = contact_number

        if 'profile_picture' in request.FILES:
            user_profile.profile_picture = request.FILES['profile_picture']

        user.username = username
        user.email = email
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']

       
        user_profile.full_clean()
        user.full_clean()
        user_profile.save()
        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('view_profile')


    data = UserProfile.objects.get(user=request.user)
    now = datetime.now()
    end_of_day = now + timedelta(days=1)
    user_rentals_next_day = Rental.objects.filter(user=request.user,return_date__range=[now, end_of_day],returned_date__isnull=True)
    rental_count = user_rentals_next_day.count()
    cart_items_count = get_cart_items_count(request)
    context={
        'user_profile': user_profile,
        'user': user,
        'data':data,
        'user_rentals_next_day': user_rentals_next_day,
        'rental_count': rental_count,
        'cart_items_count': cart_items_count,
    }
    return render(request, 'edit_profile.html', context)

@login_required(login_url='login')
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    user = request.user
    if book.stock <= 0:
        messages.info(request, f"{book.name} is out of stock.")
        return redirect('book_management_u')
    cart, created = Cart.objects.get_or_create(user=user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    if not created:
        if cart_item.quantity < book.stock:
            cart_item.quantity += 1
            cart_item.save()
            book.stock -= 1
            book.save()
        else:
            messages.warning(request, f"Sorry, you cannot add more copies of {book.name} to your cart. Stock limit reached.")
    else:
        cart_item.quantity += 0
        cart_item.save()
        book.stock -= 1
        book.save()
    return redirect('view_cart')

@login_required(login_url='login')
def update_cart(request):
    if request.method == 'POST':
        user = request.user
        cart, created = Cart.objects.get_or_create(user=user)
        book_id = request.POST.get('book_id')
        new_quantity = int(request.POST.get('new_quantity', 0))
        cart_item = CartItem.objects.get(cart=cart, book__id=book_id)
        old_quantity = cart_item.quantity
        cart_item.quantity = new_quantity
        cart_item.save()
        book = cart_item.book
        book.stock += old_quantity - new_quantity
        book.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required(login_url='login')
def remove_from_cart(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    user = request.user
    cart = Cart.objects.get(user=user)
    cart_item = CartItem.objects.get(cart=cart, book=book)
    cart_item_quantity = cart_item.quantity
    cart_item.delete()
    book.stock += cart_item_quantity
    book.save()
    return redirect('view_cart')

from django.shortcuts import render
from .models import Cart, UserProfile, Rental
from datetime import datetime, timedelta

@login_required(login_url='login')
def view_cart(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    cart_items = cart.cartitem_set.all()
    data = UserProfile.objects.get(user=request.user)
    now = datetime.now()
    end_of_day = now + timedelta(days=1)
    user_rentals_next_day = Rental.objects.filter(user=request.user, return_date__range=[now, end_of_day], returned_date__isnull=True)
    rental_count = user_rentals_next_day.count()
    
    context = {
        'data': data,
        'user_rentals_next_day': user_rentals_next_day,
        'rental_count': rental_count,
        'cart_items': cart_items,
        'cart_items_count': cart_items.count(),  # Add this line to include the count
    }
    
    return render(request, 'view_cart.html', context)



@login_required(login_url='login')
def get_cart_items_count(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    return cart.cartitem_set.count()


from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from decimal import Decimal
from datetime import datetime, timedelta
from .models import Cart, Purchase, PurchaseItem, UserProfile, Rental

@login_required(login_url='login')
def checkout(request):
    user = request.user

    cart, created = Cart.objects.get_or_create(user=user)
    cart_items = cart.cartitem_set.all()

    subtotal = sum(item.book.price * item.quantity for item in cart_items)
    tax_percentage = Decimal('0.05')  
    shipping_fee = Decimal('15.00')
    tax = subtotal * tax_percentage
    total_price = subtotal + tax + shipping_fee

    if request.method == 'POST':
        try:
            for cart_item in cart_items:
                book = cart_item.book
                quantity_key = f'quantity_{book.id}'
                new_quantity = int(request.POST.get(quantity_key, 1))

                if new_quantity <= 0 or new_quantity > cart_item.quantity:
                    messages.error(request, 'Invalid quantity selected.')
                    return redirect('checkout')

                cart_item.quantity = new_quantity
                cart_item.save()

            purchase = Purchase.objects.create(
                user=user,
                total_amount=total_price,
                billing_full_name=request.POST.get('firstname'),
                billing_email=request.POST.get('email'),
                billing_address=request.POST.get('address'),
                billing_city=request.POST.get('city'),
                billing_state=request.POST.get('state'),
                billing_zip=request.POST.get('zip'),
                shipping_full_name=request.POST.get('firstname'),
                shipping_email=request.POST.get('email'),
                shipping_address=request.POST.get('address'),
                shipping_city=request.POST.get('city'),
                shipping_state=request.POST.get('state'),
                shipping_zip=request.POST.get('zip'),
                card_name=request.POST.get('cardname'),
                card_number=request.POST.get('cardnumber'),
                expiration_month=request.POST.get('expmonth'),
                expiration_year=request.POST.get('expyear'),
                cvv=request.POST.get('cvv')
            )

            for cart_item in cart_items:
                PurchaseItem.objects.create(
                    purchase=purchase,
                    book=cart_item.book,
                    quantity=cart_item.quantity
                )

            cart_items.delete()

            subject = 'Purchase Confirmation'
            message = f"Thank you for your purchase.\n\nDetails of your purchase:\n\n"
            for item in purchase.purchaseitem_set.all():
                message += f"- {item.quantity} x {item.book.name} - {item.book.price}\n"

            message += f"\nTotal Amount: {total_price}\n" 

            message += "\nBilling Address:\n"
            message += f"{purchase.billing_full_name}\n"
            message += f"{purchase.billing_email}\n"
            message += f"{purchase.billing_address}\n"
            message += f"{purchase.billing_city}, {purchase.billing_state} {purchase.billing_zip}\n"

            send_mail(
                subject,
                message,
                'your_email@example.com', 
                [user.email], 
                html_message=None, 
            )


            messages.success(request, 'Purchase successful.')
            return redirect(reverse('thankyou', kwargs={'purchase_id': purchase.id}))

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('checkout')

    data = UserProfile.objects.get(user=request.user)

    now = datetime.now()
    end_of_day = now + timedelta(days=1)
    user_rentals_next_day = Rental.objects.filter(user=request.user, return_date__range=[now, end_of_day], returned_date__isnull=True)
    rental_count = user_rentals_next_day.count()

    cart_items_count = get_cart_items_count(request)

    context = {
    'cart_items': cart_items,
    'subtotal': subtotal,
    'tax': tax,
    'shipping': shipping_fee,
    'total_price': total_price,
    'total_amount': total_price, 
    'data': data,
    'user_rentals_next_day': user_rentals_next_day,
    'rental_count': rental_count,
    'cart_items_count': cart_items_count,
}


    return render(request, 'checkout.html', context)

def thankyou(request, purchase_id):
    purchase = get_object_or_404(Purchase, pk=purchase_id)
    data = UserProfile.objects.get(user=request.user)
    now = datetime.now()
    end_of_day = now + timedelta(days=1)
    user_rentals_next_day = Rental.objects.filter(user=request.user,return_date__range=[now, end_of_day],returned_date__isnull=True);rental_count = user_rentals_next_day.count()
    context={
        'purchase': purchase,
        'data':data,
        'user_rentals_next_day': user_rentals_next_day,
        'rental_count': rental_count
    }
    messages.success(request, 'Purchase successful.')
    return render(request, 'thankyou.html', context)

@login_required(login_url='login')
def unapproved_users(request):
    unapproved_users = UserProfile.objects.filter(is_approved=False).exclude(user__last_login__isnull=False)    
    total_unapproved_users = unapproved_users.count() 
    total_rental_dues = get_user_rentals_next_day_count()
    context = {
        'unapproved_users': unapproved_users,
        'total_unapproved_users': total_unapproved_users,
        'total_rental_dues':total_rental_dues
    }
    return render(request, 'unapproved_users.html', context)

from django.utils import timezone

@login_required(login_url='login')
def user_rentals_next_day_ad(request):
    now = timezone.now()
    overdue_rentals = Rental.objects.filter(return_date__lt=now, returned_date__isnull=True, fine_amount=0)
    total_rental_dues = overdue_rentals.count() 
    total_unapproved_users = get_unapproved_users_count()
    context = {
        'user_rentals_next_day': overdue_rentals,
        'total_rental_dues': total_rental_dues,
        "total_unapproved_users": total_unapproved_users
    }
    return render(request, 'user_rentals_next_day_ad.html', context)


def get_unapproved_users_count():
    unapproved_users = UserProfile.objects.filter(is_approved=False).exclude(user__last_login__isnull=False)    
    return unapproved_users.count()

def get_user_rentals_next_day_count():
    now = timezone.now()
    user_rentals_next_day = Rental.objects.filter(return_date__lt=now, returned_date__isnull=True, fine_amount=0)
    return user_rentals_next_day.count()

@login_required(login_url='login')
def user_rentals_next_day(request):
    data = UserProfile.objects.get(user=request.user)
    now = datetime.now()
    end_of_day = now + timedelta(days=1)
    user_rentals_next_day = Rental.objects.filter(
        user=request.user,
        return_date__range=[now, end_of_day],
        returned_date__isnull=True
    )
    rental_count = user_rentals_next_day.count() 
    cart_items_count = get_cart_items_count(request)
    context = {
        'data': data,
        'user_rentals_next_day': user_rentals_next_day,
        'rental_count': rental_count,
        'cart_items_count': cart_items_count,
    }
    return render(request, 'user_rentals_next_day.html', context)


def purchase_history(request):
    user_purchases = Purchase.objects.filter(user=request.user).order_by('-purchase_date')
    data = UserProfile.objects.get(user=request.user)
    now = datetime.now()
    end_of_day = now + timedelta(days=1)
    user_rentals_next_day = Rental.objects.filter(user=request.user,return_date__range=[now, end_of_day],returned_date__isnull=True);rental_count = user_rentals_next_day.count()
    context = {
        'user_purchases': user_purchases,
        'data':data,
        'user_rentals_next_day': user_rentals_next_day,
        'rental_count': rental_count,
    }
    return render(request, 'purchase_history.html', context)

from django.shortcuts import render, get_object_or_404
from .models import Book

def book_detail(request, book_id):    
    book = get_object_or_404(Book, pk=book_id)
    data = UserProfile.objects.get(user=request.user)
    now = datetime.now()
    end_of_day = now + timedelta(days=1)
    user_rentals_next_day = Rental.objects.filter(user=request.user,return_date__range=[now, end_of_day],returned_date__isnull=True);rental_count = user_rentals_next_day.count()
    cart_items_count = get_cart_items_count(request)
    context={
        'data':data,
        'user_rentals_next_day': user_rentals_next_day,
        'rental_count': rental_count,
        'book': book,
        'cart_items_count': cart_items_count,
    }
    return render(request, 'book_detail.html',context)

@login_required(login_url='login')
def rent_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if book.stock <= 0:
        messages.info(request, f"{book.name} is out of stock.")
        return redirect('book_management_u')
    if request.method == 'POST':
        rental_date_str = request.POST.get('rental_date')
        return_date_str = request.POST.get('return_date')
        try:
            rental_date = datetime.strptime(rental_date_str, '%Y-%m-%d').date()
            return_date = datetime.strptime(return_date_str, '%Y-%m-%d').date()
            if book.stock > 0 and rental_date <= return_date:

                rental_request = Rental.objects.create(
                    user=request.user,
                    book=book,
                    rental_date=rental_date,
                    return_date=return_date,
                    is_rental_request=True
                )
                rental_request.save()
                messages.success(request, 'Rental request sent successfully. Wait for admin approval.')
                return redirect('rental_requests')
            elif book.stock <= 0:
                messages.error(request, 'Sorry, the selected book is not available for rental.')
            else:
                messages.error(request, 'Invalid rental and return dates. Return date must be after or equal to rental date.')
        except ValueError:
            messages.error(request, 'Invalid date format.')

    default_rental_date = timezone.now().date()
    data = UserProfile.objects.get(user=request.user)
    now = datetime.now()
    end_of_day = now + timedelta(days=1)
    user_rentals_next_day = Rental.objects.filter(user=request.user, return_date__range=[now, end_of_day],
        returned_date__isnull=True)
    rental_count = user_rentals_next_day.count()
    cart_items_count = get_cart_items_count(request)

    context = {
        'book': book,
        'default_rental_date': default_rental_date,
        'data': data,
        'user_rentals_next_day': user_rentals_next_day,
        'rental_count': rental_count,
        'cart_items_count': cart_items_count,
    }
    return render(request, 'rent_book.html', context)

from django.db import transaction

@login_required(login_url='login')
def return_book(request, rental_id):
    rental = get_object_or_404(Rental, pk=rental_id)
    if request.method == 'POST':
        # Use a transaction to ensure atomicity
        with transaction.atomic():
            # Update the existing rental object with the return request
            rental.is_return_request = True
            rental.save()
        messages.success(request, 'Return request sent successfully. Wait for admin approval.')
        return redirect('return_requests')
    return render(request, 'return_book.html', {'rental': rental})


from django.shortcuts import render
from .models import Rental, Notification

@login_required(login_url='login')
def rental_requests(request):
    user_rental_requests = Rental.objects.filter(user=request.user, is_rental_request=True)
    data = UserProfile.objects.get(user=request.user)
    now = datetime.now()
    end_of_day = now + timedelta(days=1)
    user_rentals_next_day = Rental.objects.filter(user=request.user,return_date__range=[now, end_of_day],returned_date__isnull=True);rental_count = user_rentals_next_day.count()
    cart_items_count = get_cart_items_count(request)
    context = {
        'user_rental_requests': user_rental_requests,
        'data':data,
        'user_rentals_next_day': user_rentals_next_day,
        'rental_count': rental_count,'cart_items_count': cart_items_count,
    }
    return render(request, 'rental_requests.html', context)

@login_required(login_url='login')
def return_requests(request):
    user_return_requests = Rental.objects.filter(user=request.user, is_return_request=True)
    data = UserProfile.objects.get(user=request.user)
    now = datetime.now()
    end_of_day = now + timedelta(days=1)
    user_rentals_next_day = Rental.objects.filter(user=request.user,return_date__range=[now, end_of_day],returned_date__isnull=True);rental_count = user_rentals_next_day.count()
    
    cart_items_count = get_cart_items_count(request)
    context = {
        'user_return_requests': user_return_requests,
        'data':data,
        'user_rentals_next_day': user_rentals_next_day,
        'rental_count': rental_count,
        'cart_items_count': cart_items_count,
    }
    return render(request, 'return_requests.html', context)


from django.db.models import Q
@login_required(login_url='login')
def rental_history(request):
    user = request.user
    current = request.user.id
    data = UserProfile.objects.get(user_id=current) 
    rental_history = Rental.objects.filter(
        Q(user=user, is_rental_approved=True) | Q(user=user, is_return_approved=True)
    ).order_by('-id') 
    now = datetime.now()
    end_of_day = now + timedelta(days=1)
    user_rentals_next_day = Rental.objects.filter(
        user=request.user,
        return_date__range=[now, end_of_day],
        returned_date__isnull=True
    )
    rental_count = user_rentals_next_day.count()
    cart_items_count = get_cart_items_count(request)
    context = {
        'user_rentals_next_day': user_rentals_next_day,
        'rental_count': rental_count,
        'data': data,
        'rental_history': rental_history,
        'now':now,
        'cart_items_count': cart_items_count,
    }
    return render(request, 'rental_history.html', context)



################    admin   ##############################################################################################################

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Book, Rental, Notification, UserProfile, User

@login_required(login_url='login')
def rental_requests_admin(request):
    if not request.user.is_staff:
        return redirect('home')
    rental_requests = Rental.objects.filter(is_rental_request=True, is_rental_approved=False)
    total_rental_dues = get_user_rentals_next_day_count()
    total_unapproved_users = get_unapproved_users_count()

    context = {
        'rental_requests': rental_requests,
        "total_rental_dues": total_rental_dues,
        "total_unapproved_users" : total_unapproved_users

    }
    return render(request, 'rental_requests_admin.html', context)

@login_required(login_url='login')
def return_requests_admin(request):
    if not request.user.is_staff:
        return redirect('home')
    return_requests = Rental.objects.filter(is_return_request=True, is_return_approved=False)
    total_rental_dues = get_user_rentals_next_day_count()
    total_unapproved_users = get_unapproved_users_count()
    context = {
        'return_requests': return_requests,
        "total_rental_dues": total_rental_dues,
        "total_unapproved_users" : total_unapproved_users
    }
    return render(request, 'return_requests_admin.html', context)

from django.db import transaction

@login_required(login_url='login')
def approve_rental_request(request, rental_id):
    if not request.user.is_staff:
        return redirect('home')
    
    with transaction.atomic():
        rental_request = get_object_or_404(Rental, pk=rental_id, is_rental_request=True, is_rental_approved=False)
        rental_request.is_rental_approved = True
        rental_request.save()

        # Decrease book stock by 1 when rental request is approved
        book = rental_request.book
        book.stock -= 1
        book.save()

    messages.success(request, 'Rental request approved successfully.')
 

    return redirect('rental_requests_admin')

@login_required(login_url='login')
def approve_return_request(request, rental_id):
    if not request.user.is_staff:
        return redirect('home')

    with transaction.atomic():
        return_request = get_object_or_404(Rental, pk=rental_id, is_return_request=True, is_return_approved=False)
        return_request.is_return_approved = True
        return_request.save()

        # Increase book stock by 1 when return request is approved
        book = return_request.book
        book.stock += 1
        book.save()

    messages.success(request, 'Return request approved successfully.')

 
    return redirect('return_requests_admin')

from django.db.models import Q
@login_required(login_url='login')
def view_user_rental_history(request):
    user_id = request.GET.get('user_id')
    user_profile = get_object_or_404(UserProfile, pk=user_id)
    rentals = Rental.objects.filter(
    Q(user=user_profile.user,is_rental_approved=True) | Q(user=user_profile.user,is_return_approved=True))
    total_rental_dues = get_user_rentals_next_day_count()
    total_unapproved_users = get_unapproved_users_count()
    now = datetime.now()
    context = {
        'user': user_profile,
        'rentals': rentals,
        'total_rental_dues': total_rental_dues,
        'total_unapproved_users': total_unapproved_users,
        'now': now
    }
    return render(request, 'view_user_rental_history.html', context)
