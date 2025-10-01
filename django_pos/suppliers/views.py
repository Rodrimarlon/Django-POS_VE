from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Supplier
from .forms import SupplierForm
from authentication.decorators import admin_required
from django.db import IntegrityError
