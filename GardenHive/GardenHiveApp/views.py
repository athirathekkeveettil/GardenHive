from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.models import User 
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image
from .models import UserProfile
from .models import Nursery, Staff
from .models import Login
from .models import Category, Subcategory
from .models import CareTip
from .models import Product
from .models import Cart, Booking
from django.contrib import messages
from django.urls import reverse

import os
import json
import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras.preprocessing import image 
from django.core.files.storage import FileSystemStorage
from django.utils import timezone 
from decimal import Decimal
# Create your views here.

def index(request):
    return render(request,"index.html")


def nurseryRegister(request):
    """ Register new nursery with location """
    
    if request.method == 'POST':
        name = request.POST['name']
        address = request.POST['address']
        location = request.POST['location']  # ✅ Capture location
        owner = request.POST['owner']
        lcnno = request.POST['lcnno']
        email = request.POST['email']
        phone = request.POST['phone']
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("nurseryRegister")

        if Login.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken!")
            return redirect("nurseryRegister")

        if Nursery.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered!")
            return redirect("nurseryRegister")

        login = Login.objects.create(username=username, password=password, types='nursery', status='0')

        nursery = Nursery.objects.create(
            name=name,
            addr=address,
            location=location,  
            owner=owner,
            lcnno=lcnno,
            email=email,
            phno=phone,
            username=username,
            logid=login,
            status='0'
        )

        login.save()
        nursery.save()

        messages.success(request, "Registration successful! Waiting for admin approval.")
        return redirect("nurseryRegister")

    return render(request, 'nurseryRegister.html')

def userRegister(request):
    if request.method == "POST":
        name = request.POST["name"]
        address = request.POST["address"]
        gender = request.POST["gender"]
        location = request.POST["location"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        username = request.POST["username"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("userRegister")

        if Login.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken!")
            return redirect("userRegister")
        if Login.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered!")
            return redirect("userRegister")

        login_instance = Login.objects.create(
            username=username, 
            password=password, 
            types="user", 
            status="1"  
        )

        user_profile = UserProfile.objects.create(
            logid=login_instance,
            name=name,
            address=address,
            gender=gender,
            location=location,
            email=email,
            phone=phone
        )

        messages.success(request, "Registration successful! You can now log in.")
        return redirect("login")

    return render(request, "userRegister.html")


def login_view(request):
    """ Handle user login and store nursery ID in session """

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, "Both username and password are required!")
            return redirect("login")

        if username == "admin" and password == "123":
            request.session['username'] = username
            request.session['user_type'] = "admin"
            return redirect("/adminhome") 

        try:
            user = Login.objects.get(username=username, password=password)

            request.session['username'] = user.username
            request.session['user_type'] = user.types

            if user.types == "admin":
                return redirect("/adminhome")

            elif user.types == "nursery":
                try:
                    # ✅ Retrieve the associated nursery and store its ID in session
                    nursery = Nursery.objects.get(logid=user)
                    request.session['nursery_id'] = nursery.id  # Store nursery ID
                    request.session['nursery_name'] = nursery.name  # Store nursery name (optional)

                    messages.success(request, f"Welcome, {nursery.name}!")
                    return redirect("/nurseryhome")

                except Nursery.DoesNotExist:
                    messages.error(request, "No nursery associated with this account.")
                    return redirect("login")

            elif user.types == "user":
                return redirect("/userhome")

        except Login.DoesNotExist:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    return render(request, "login.html")

def adminapprovenursery(request):
    nurseries = Nursery.objects.filter(status="0") 
    return render(request, "adminapprovenursery.html", {"nurseries": nurseries})

def approve_nursery(request, nursery_id):
    try:
        nursery = get_object_or_404(Nursery, id=nursery_id)

        nursery.status = "1"
        nursery.save()

        if nursery.logid:
            login_instance = get_object_or_404(Login, id=nursery.logid.id)
            login_instance.status = "1"
            login_instance.save()

        messages.success(request, "Nursery approved successfully!")
    except Exception as e:
        messages.error(request, f"Error approving nursery: {e}")

    return redirect("adminapprovenursery")

def reject_nursery(request, nursery_id):
    try:
        nursery = get_object_or_404(Nursery, id=nursery_id)
        nursery.status = "-1" 
        nursery.save()

        if nursery.logid:
            login_instance = get_object_or_404(Login, id=nursery.logid.id)
            login_instance.status = "-1"
            login_instance.save()

        messages.error(request, "Nursery rejected successfully!")
    except Exception as e:
        messages.error(request, f"Error rejecting nursery: {e}")

    return redirect("adminapprovenursery")

def register(request):
    return render(request,"register.html")

def adminhome(request):
    return render(request,"adminhome.html")

def admin_manage_accounts(request):
    selected_type = request.GET.get("type") 
    users = User.objects.all().order_by('-date_joined') if selected_type == "user" else None
    nurseries = Nursery.objects.filter(status="1") if selected_type == "nursery" else None  

    return render(request, "admin_manage_accounts.html", {"users": users, "nurseries": nurseries, "selected_type": selected_type})
    
def delete_user(request, user_id):
    try:
        
        user = Login.objects.filter(id=user_id).first()

        if user:
            if user.types == "nursery":
                nursery = Nursery.objects.filter(logid=user).first()
                if nursery:
                    nursery.delete()
            user.delete()  
            messages.success(request, "User/Nursery deleted successfully!")
        else:
            messages.error(request, "User/Nursery not found!")

    except Exception as e:
        messages.error(request, f"Error deleting user/nursery: {e}")

    return redirect("admin_manage_accounts")

def delete_nursery(request, nursery_id):
    nursery = get_object_or_404(Nursery, id=nursery_id)
    nursery.delete()
    messages.success(request, "Nursery deleted successfully!")
    return redirect("admin_manage_accounts")

def admin_category(request):
    categories = Category.objects.all() 
    return render(request, "admin_category.html", {"categories": categories})

def admin_category(request):
    if request.method == "POST":
        name = request.POST.get("name").strip()
        description = request.POST.get("description").strip()

        if not name:
            messages.error(request, "Category name is required!")
            return redirect("admin_category")

        if Category.objects.filter(name=name).exists():
            messages.error(request, "Category already exists!")
        else:
            Category.objects.create(name=name, description=description)
            messages.success(request, "Category added successfully!")

    categories = Category.objects.all().order_by('-created_at') 
    return render(request, "admin_category.html", {"categories": categories})
    
def update_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        category.name = request.POST.get("name").strip()
        category.description = request.POST.get("description").strip()
        category.save()
        messages.success(request, "Category updated successfully!")
        return redirect("admin_category")

    return render(request, "edit_category.html", {"category": category})

def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.success(request, "Category deleted successfully!")
    return redirect("admin_category")

def admin_subcategory(request):
    if request.method == 'POST':
        category_id = request.POST.get('category')
        name = request.POST.get('name')
        description = request.POST.get('description')

        category = Category.objects.get(id=category_id)

        Subcategory.objects.create(
            category=category,
            name=name,
            description=description
        )

        messages.success(request, 'Subcategory added successfully!')
        return redirect('admin_subcategory')

    categories = Category.objects.all()
    subcategories = Subcategory.objects.select_related('category').all()

    context = {
        'categories': categories,
        'subcategories': subcategories
    }
    
    return render(request, 'admin_subcategory.html', context)

def update_subcategory(request, subcategory_id):
   
    subcategory = get_object_or_404(Subcategory, id=subcategory_id)

    categories = Category.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        category_id = request.POST.get('category')

        subcategory.name = name
        subcategory.description = description
        subcategory.category = get_object_or_404(Category, id=category_id)
        subcategory.save()

        messages.success(request, 'Subcategory updated successfully!')
        return redirect('admin_subcategory')

    context = {
        'subcategory': subcategory,
        'categories': categories  
    }

    return render(request, 'edit_subcategory.html', context)

def delete_subcategory(request, subcategory_id):
    subcategory = get_object_or_404(Subcategory, id=subcategory_id)
    subcategory.delete()
    messages.success(request, 'Subcategory deleted successfully!')
    return redirect('admin_subcategory')

def admin_care_tips(request):
    categories = Category.objects.all() 
    care_tips = CareTip.objects.all().order_by('-created_at') 

    if request.method == "POST":
        category_id = request.POST.get("category")
        title = request.POST.get("title").strip()
        description = request.POST.get("description").strip()

        if not title:
            messages.error(request, "Title is required!")
            return redirect("admin_care_tips")

        if CareTip.objects.filter(title=title).exists():
            messages.error(request, "Care Tip already exists!")
        else:
            category = get_object_or_404(Category, id=category_id)
            CareTip.objects.create(category=category, title=title, description=description)
            messages.success(request, "Care Tip added successfully!")

    return render(request, "admin_care_tips.html", {"care_tips": care_tips, "categories": categories})

def update_care_tip(request, care_tip_id):
    care_tip = get_object_or_404(CareTip, id=care_tip_id)
    categories = Category.objects.all()

    if request.method == "POST":
        care_tip.category = get_object_or_404(Category, id=request.POST.get("category"))
        care_tip.title = request.POST.get("title").strip()
        care_tip.description = request.POST.get("description").strip()
        care_tip.save()
        messages.success(request, "Care Tip updated successfully!")
        return redirect("admin_care_tips")

    return render(request, "edit_care_tips.html", {"care_tip": care_tip, "categories": categories})

def delete_care_tip(request, care_tip_id):
    care_tip = get_object_or_404(CareTip, id=care_tip_id)
    care_tip.delete()
    messages.success(request, "Care Tip deleted successfully!")
    return redirect("admin_care_tips")

def nurseryhome(request):
   
    if "username" not in request.session:
        return redirect("login")  

    username = request.session["username"]

    try:
        logged_in_user = Login.objects.get(username=username)
        nursery = Nursery.objects.get(logid=logged_in_user) 
    except (Login.DoesNotExist, Nursery.DoesNotExist):
        return redirect("login") 

    return render(request, "nurseryhome.html", {"nursery": nursery})

def add_staff(request, nursery_id):
    nursery = get_object_or_404(Nursery, id=nursery_id)

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        role = request.POST.get('role')
        image = request.FILES.get('image')

        # Create staff instance
        staff = Staff(
            nursery=nursery,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            role=role,
            image=image
        )
        staff.save()

        messages.success(request, 'Staff added successfully!')

        # ✅ Redirect with nursery_id explicitly
        return redirect('staff_list', nursery_id=nursery.id)

    return render(request, 'add_staff.html', {'nursery': nursery})

@login_required
def staff_list(request, nursery_id):
    nursery = get_object_or_404(Nursery, id=nursery_id)
    staff = Staff.objects.filter(nursery=nursery)
    
    return render(request, 'staff_list.html', {'staff': staff, 'nursery': nursery})

@login_required
def add_product(request):
    """ Add product by the logged-in nursery """

    try:
        nursery = Nursery.objects.get(id=request.session.get('nursery_id')) 
    except Nursery.DoesNotExist:
        messages.error(request, "Nursery not found. Please log in as a nursery.")
        return redirect('index')

    if request.method == 'POST':

        name = request.POST.get('name')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('subcategory')
        size = request.POST.get('size', '')
        image = request.FILES.get('image')

        if not (name and price and category_id):
            messages.error(request, "Please fill in all required fields.")
            return redirect('add_product')

        try:

            category = Category.objects.get(id=category_id)
            subcategory = Subcategory.objects.get(id=subcategory_id) if subcategory_id else None

            product = Product(
                name=name,
                description=description,
                price=price,
                category=category,
                subcategory=subcategory,
                size=size,
                image=image,
                nursery=nursery 
            )
            product.save()

            messages.success(request, "Product added successfully!")
            return redirect('my_products') 

        except (Category.DoesNotExist, Subcategory.DoesNotExist):
            messages.error(request, "Invalid category or subcategory.")
            return redirect('add_product')

    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()

    context = {
        'categories': categories,
        'subcategories': subcategories
    }

    return render(request, 'add_product.html', context)


def product_list(request):
    """ Display products added by the logged-in nursery """

    # ✅ Get the logged-in nursery ID from session
    nursery_id = request.session.get('nursery_id')

    if not nursery_id:
        messages.error(request, "You need to be logged in as a nursery to view products.")
        return redirect("nurseryLogin")

    try:
        # ✅ Retrieve the nursery and its products
        nursery = Nursery.objects.get(id=nursery_id)
        products = Product.objects.filter(nursery=nursery)  # Filter by nursery

    except Nursery.DoesNotExist:
        messages.error(request, "Nursery not found.")
        products = []

    context = {
        'nursery': nursery,
        'products': products
    }

    return render(request, 'my_products.html', context)

def manage_products(request):
    if "username" not in request.session:
        return redirect("login")  

    username = request.session["username"]
    try:
        nursery = Nursery.objects.get(logid__username=username) 
        products = Product.objects.filter(nursery=nursery) 
    except Nursery.DoesNotExist:
        messages.error(request, "No nursery profile found!")
        return redirect("login")

    return render(request, "manage_products.html", {"products": products})

def edit_product(request, product_id):
    """ Edit product by ID """
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.size = request.POST.get('size')

        if 'image' in request.FILES:
            product.image = request.FILES['image']

        product.save()
        messages.success(request, "Product updated successfully!")
        return redirect('product_list')

    context = {
        'product': product
    }
    return render(request, 'edit_product.html', context)

def delete_product(request, product_id):
    """ Delete product by ID """
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect('product_list')

@login_required
def nursery_products(request):
    """ Display products only from the logged-in nursery """

    try:
        nursery = Nursery.objects.get(user=request.user)
        products = Product.objects.filter(nursery=nursery)
    except Nursery.DoesNotExist:
        messages.error(request, "You are not associated with any nursery.")
        return redirect('home')

    context = {
        'products': products
    }
    return render(request, 'nursery_products.html', context)

def userhome(request):
    search_query = request.GET.get("search", "").strip()  
    selected_nursery_id = request.GET.get("nursery")  
    selected_category_id = request.GET.get("category")  

    categories = Category.objects.all()
    nurseries = Nursery.objects.all()  
    products = Product.objects.all() 

    if search_query:
        products = Product.objects.filter(name__icontains=search_query)

    if selected_category_id:
        products = products.filter(category_id=selected_category_id)

    if selected_nursery_id:
        products = products.filter(nursery_id=selected_nursery_id)

    context = {
        "categories": categories,
        "nurseries": nurseries,
        "products": products,
        "search_query": search_query,
        "selected_nursery_id": selected_nursery_id,
        "selected_category_id": selected_category_id,
    }
    
    return render(request, "userhome.html", context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)

    if created:
        messages.success(request, f"{product.name} added to cart.")
    else:
        messages.info(request, f"{product.name} is already in your cart.")

    return redirect('all_products')

@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.price for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'view_cart.html', context)

def payment_page(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == "POST":
        booking.status = "Paid"
        booking.save()
        messages.success(request, "Payment successful! Your order has been placed.")
        return redirect("userhome")  

    return render(request, "payment_page.html", {"booking": booking})

def care_tips(request):
    categories = Category.objects.all()
    care_tips = None

    if request.method == "GET" and "category" in request.GET:
        category_id = request.GET.get("category")
        if category_id:
            category = get_object_or_404(Category, id=category_id)
            care_tips = CareTip.objects.filter(category=category)

    return render(request, "care_tips.html", {"categories": categories, "care_tips": care_tips})

def product_search(request):
    query = request.GET.get("query", "").strip()
    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)  # Search by product name only

    return render(request, "product_search.html", {
        "products": products,
        "query": query
    })

def search_nursery(request):
    query = request.GET.get("query", "").strip()
    nurseries = Nursery.objects.filter(name__icontains=query) if query else Nursery.objects.all()

    nursery_products = {}
    for nursery in nurseries:
        products = Product.objects.filter(nursery=nursery)
        nursery_products[nursery] = products

    return render(request, "search_nursery.html", {"nurseries": nurseries, "nursery_products": nursery_products, "query": query})

def search_products(request):
    query = request.GET.get("query", "").strip()
    search_results = []

    if query:
        search_results = Product.objects.filter(
            Q(name__icontains=query) |  
            Q(category__name__icontains=query) |  
            Q(nursery__name__icontains=query) |  
            Q(nursery__addr__icontains=query)  
        )

    if request.FILES.get("image"):
        uploaded_image = request.FILES["image"]
        image_path = default_storage.save(f"search_images/{uploaded_image.name}", uploaded_image)

        search_results = Product.objects.filter(image=uploaded_image.name)  

    return render(request, "search_results.html", {"products": search_results, "query": query})

MODEL_PATH = os.path.join("GardenHiveApp", "dl_models", "PlantClassification.keras")
model = tf.keras.models.load_model(MODEL_PATH)

# Load label map (Ensure you have a label_map.json file)
LABEL_MAP_PATH = os.path.join("GardenHiveApp", "dl_models", "label_map.json")
with open(LABEL_MAP_PATH, "r") as f:
    label_map = json.load(f)

def get_label(predicted_index):
    """Convert predicted class index to human-readable label."""
    return label_map.get(str(predicted_index), "Unknown Plant")


def preprocess_image(image_path):
    """Preprocess image for CNN model"""
    img = cv2.imread(image_path)
    img = cv2.resize(img, (224, 224))  # Resize based on model input
    img = np.expand_dims(img, axis=0)  # Expand dims for batch processing
    img = img / 255.0  # Normalize
    return img

def extract_features(image_path):
    """Extract feature vector from the image using trained CNN"""
    img = preprocess_image(image_path)
    features = model.predict(img)  # Extract features
    return features.flatten()  # Convert to 1D array


def image_search(request):
    if request.method == "POST" and request.FILES.get("image"):
        uploaded_file = request.FILES["image"]

        upload_dir = "uploads/"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        file_path = os.path.join(upload_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        img = image.load_img(file_path, target_size=(224, 224))  # Resize to model's input size
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0  # Normalize

        model = tf.keras.models.load_model("dl_models/PlantClassification.keras")  
        predictions = model.predict(img_array)
        predicted_class_index = np.argmax(predictions)  # Get the highest probability class

        with open("dl_models/label_map.json", "r") as f:
            label_map = json.load(f)

        predicted_class = label_map[str(predicted_class_index)]

        matching_products = Product.objects.filter(name__icontains=predicted_class)

        return render(request, "image_search_results.html", {"products": matching_products, "predicted_class": predicted_class})

    return render(request, "image_search.html")

def predict_image(image):
    image = preprocess_image(image)  # Function to resize/normalize image
    prediction = model.predict(np.expand_dims(image, axis=0))
    predicted_index = np.argmax(prediction)  # Get highest probability index
    plant_name = get_label(predicted_index)  # Convert index to label
    return plant_name

def about(request):
    return render(request,"about.html")

def service(request):
    return render(request,"service.html")

@login_required
def all_products(request):
    products = Product.objects.all()
    return render(request, 'all_product.html', {'products': products})

def book_from_cart(request):
    if request.method == 'POST':
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items:
            messages.error(request, "Your cart is empty.")
            return redirect('cart')

        # Create a booking entry for each product in the cart
        for item in cart_items:
            Booking.objects.create(
                user=request.user,
                product=item.product,
                status='pending'
            )
        
        # Clear the cart after booking
        cart_items.delete()

        messages.success(request, "Products booked successfully!")
        return redirect('view_booking')

    return redirect('cart')

@login_required
def book_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    # Convert Decimal to int
    total_price_int = int(total_price)

    if request.method == "POST":
        return redirect('payment', total_price=total_price_int)

    return render(request, 'proceed_to_booking.html', {'cart_items': cart_items, 'total_price': total_price_int})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to add items to the cart.")
        return redirect('login') 

    cart_item, created = Cart.objects.get_or_create(
        user=request.user, 
        product=product,
        defaults={'added_at': timezone.now()}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, "Product added to cart successfully!")
    return redirect('cart')

def remove_from_cart(request, item_id):
    """ Remove an item from the cart """
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    cart_item.delete()

    return redirect('cart')


def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

def user_bookings(request):
    """ Display all bookings made by the logged-in user """
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'bookings': bookings
    }
    return render(request, 'user_bookings.html', context)

@login_required
def checkout_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    
    if not cart_items:
        return render(request, 'empty_cart.html')

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, 'checkout.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def booking_success(request):
    """ Booking Success Page """
    return render(request, 'booking_success.html')

@login_required
def payment(request, total_price):
    return render(request, 'payment.html', {'total_price': total_price})

@login_required
def payment_success(request):
    if request.method == "POST":
        
        return render(request, 'payment_success.html')
    
    return redirect('cart')

def view_bookings(request):
    """Display user's bookings with cancel option."""
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'view_bookings.html', {'bookings': bookings})


def cancel_booking(request, booking_id):
    """Handle booking cancellation if within 10 days."""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.can_cancel():
        booking.delete()
        message = "Booking canceled successfully."
    else:
        message = "Booking cannot be canceled as the 10-day period has passed."

    return render(request, 'booking_canceled.html', {'message': message})

@login_required
def proceed_to_booking(request):
    """Display the booking page with product details and quantity selection"""
    
    # Get the cart items for the current user
    cart_items = Cart.objects.filter(user=request.user)

    # Calculate the total price
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, 'proceed_to_booking.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


@login_required
def confirm_booking(request):
    """Confirm the booking, save details, and redirect to payment"""
    
    if request.method == 'POST':
        cart_items = Cart.objects.filter(user=request.user)

        total_price = 0

        # Save the booking with final quantities
        booking = Booking(user=request.user, total_price=0)
        booking.save()

        for item in cart_items:
            new_quantity = int(request.POST.get(f'quantity_{item.id}', item.quantity))
            item.quantity = max(1, new_quantity)
            item.save()

            # Add products to the booking
            booking.products.add(item.product)
            
            # Calculate the total price
            total_price += item.product.price * item.quantity

        booking.total_price = total_price
        booking.save()

        # Redirect to the payment page with the total price
        return redirect('payment', total_price=total_price)

    return redirect('proceed_to_booking')

@login_required
def nursery_bookings(request, nursery_id):
    """
    Display all bookings for a specific nursery.
    """
    nursery = get_object_or_404(Nursery, id=nursery_id)
    
    # Filter bookings by nursery through the Product relationship
    bookings = Booking.objects.filter(product__nursery=nursery)

    return render(request, 'nursery_bookings.html', {
        'nursery': nursery,
        'bookings': bookings
    })
# Edit Staff 
def edit_staff(request, nursery_id, staff_id):
    nursery = get_object_or_404(Nursery, id=nursery_id)
    staff = get_object_or_404(Staff, id=staff_id, nursery=nursery)

    if request.method == 'POST':
        staff.first_name = request.POST.get('first_name')
        staff.last_name = request.POST.get('last_name')
        staff.email = request.POST.get('email')
        staff.phone = request.POST.get('phone')
        staff.role = request.POST.get('role')

        if 'image' in request.FILES:
            staff.image = request.FILES['image']

        staff.save()
        messages.success(request, 'Staff details updated successfully!')
        return redirect('staff_list', nursery_id=nursery_id)

    return render(request, 'edit_staff.html', {'staff': staff, 'nursery': nursery})


# Delete Staff
def delete_staff(request, nursery_id, staff_id):
    nursery = get_object_or_404(Nursery, id=nursery_id)
    staff = get_object_or_404(Staff, id=staff_id, nursery=nursery)

    staff.delete()
    messages.success(request, 'Staff member deleted successfully!')
    return redirect('staff_list', nursery_id=nursery_id)

