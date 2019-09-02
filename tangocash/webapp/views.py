from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group

from django.contrib.gis.geoip2 import GeoIP2
from ipware import get_client_ip

from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

from django.utils import timezone

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse

from webapp.models import Advertisement, Review, Currency
from webapp.forms import RegisterForm, AdForm, SearchAdsForm, ReviewForm, ImportReputationForm
from webapp.functions import get_verification_code, verfiy_localbitcoins, get_google_autocomplete_locations, get_google_location

from django.template import loader

def index(request):
    # latest_trader_list = Group.objects.get(name="User")
    latest_trader_list = User.objects.order_by('-date_joined')[:5]
    context = {
        'latest_trader_list': latest_trader_list,
    }
    return render(request, 'webapp/index.html', context)

def detail(request, username):
    trader = get_object_or_404(User, username=username)
    return render(request, 'webapp/detail.html', {'trader': trader})

def buy_ads(request):
    ads_list = Advertisement.objects.filter(selling=True)
    location = None

    if request.method == 'POST':
        # Search by location or currency
        form = SearchAdsForm(request.POST)
        
        if form.is_valid():
            # Validate place_id and get details
            place_details = get_google_location(form.cleaned_data["place_id"], request.session)   

            if place_details is None:
                messages.info(request, f'Invalid place')
            else:
                # Filter currencies first
                if form.cleaned_data['currency'] != 'any':
                    ads_list = ads_list.filter(currency=form.cleaned_data['currency'])

                selected_location = Point(place_details['geometry']['location']['lng'], place_details['geometry']['location']['lat'], srid=4326)
                location = form.cleaned_data['location']

                # Filter ads outside radius and order by distance
                ads_list = ads_list.filter(
                    location_point__distance_lt=(selected_location, D(km=form.cleaned_data['radius']))
                ).annotate(
                    distance=Distance('location_point', selected_location)
                ).order_by('distance')

        # In either case, render the page with the results
        # If the form is valid, ads_list will be filtered
        # If form is not valid, form will contain errors
        context = {
            'ads_list': ads_list,
            'form': form,
            'location': location
        }
        return render(request, 'webapp/buy_ads.html', context)
    else:
        
        # Attempt to filter based on location
        ip, is_routable = get_client_ip(request)
        location = ''

        if ip is not None:
            if is_routable:
                # The IP address is publicly routable on the Internet
                user_location = GeoIP2().city(ip)
                selected_location = Point(user_location['longitude'], user_location['latitude'], srid=4326)
                location = f'{user_location["city"]}, {user_location["country_name"]}'

                # Filter ads outside radius and order by distance
                ads_list = ads_list.filter(
                    location_point__distance_lt=(selected_location, D(km=500))
                ).annotate(
                    distance=Distance('location_point', selected_location)
                ).order_by('distance')
            else:
                # The IP address is private
                print(ip)
                print('ip address is private - skipping filtering')

        context = {
            'ads_list': ads_list,
            'form': SearchAdsForm(),
            'location': location
        }
        return render(request, 'webapp/buy_ads.html', context)

def sell_ads(request):
    ads_list = Advertisement.objects.filter(selling=False)
    location = None

    if request.method == 'POST':
        # Search by location or currency
        form = SearchAdsForm(request.POST)
        
        if form.is_valid():
            # Validate place_id and get details
            place_details = get_google_location(form.cleaned_data["place_id"], request.session)   

            if place_details is None:
                messages.info(request, f'Invalid place')
            else:
                # Filter currencies first
                if form.cleaned_data['currency'] != 'any':
                    ads_list = ads_list.filter(currency=form.cleaned_data['currency'])

                selected_location = Point(place_details['geometry']['location']['lng'], place_details['geometry']['location']['lat'], srid=4326)
                location = form.cleaned_data['location']

                # Filter ads outside radius and order by distance
                ads_list = ads_list.filter(
                    location_point__distance_lt=(selected_location, D(km=form.cleaned_data['radius']))
                ).annotate(
                    distance=Distance('location_point', selected_location)
                ).order_by('distance')

        # In either case, render the page with the results
        # If the form is valid, ads_list will be filtered
        # If form is not valid, form will contain errors
        context = {
            'ads_list': ads_list,
            'form': form,
            'location': location
        }
        return render(request, 'webapp/sell_ads.html', context)
    else:
        
        # Attempt to filter based on location
        ip, is_routable = get_client_ip(request)
        location = ''

        if ip is not None:
            if is_routable:
                # The IP address is publicly routable on the Internet
                user_location = GeoIP2().city(ip)
                selected_location = Point(user_location['longitude'], user_location['latitude'], srid=4326)
                location = f'{user_location["city"]}, {user_location["country_name"]}'

                # Filter ads outside radius and order by distance
                ads_list = ads_list.filter(
                    location_point__distance_lt=(selected_location, D(km=500))
                ).annotate(
                    distance=Distance('location_point', selected_location)
                ).order_by('distance')
            else:
                # The IP address is private
                print(ip)
                print('ip address is private - skipping filtering')

        context = {
            'ads_list': ads_list,
            'form': SearchAdsForm(),
            'location': location
        }
        return render(request, 'webapp/sell_ads.html', context)

def ad_detail(request, ad_id):
    ad = get_object_or_404(Advertisement, pk=ad_id)
    return render(request, 'webapp/advertisement.html', {'ad': ad})

@login_required
def new_ad(request):
    if request.method == 'POST':
        form = AdForm(request.POST)
        if form.is_valid():
            
            # Validate place_id and get details
            place_details = get_google_location(form.cleaned_data["place_id"], request.session)            
            if place_details is None:
                messages.info(request, f'Invalid place')
                return render(request, 'webapp/new_ad.html', {'form': form})

            # Add ad to database
            ad_object = Advertisement(
                trader=request.user,
                post_date=timezone.now(),
                ad_text=form.cleaned_data["ad_text"],
                currency=get_object_or_404(Currency, pk=form.cleaned_data["currency"]),
                location_point=Point(place_details['geometry']['location']['lng'], place_details['geometry']['location']['lat'], srid=4326),
                location_name=place_details['formatted_address'],
                location_place_id=form.cleaned_data["place_id"],
                selling=form.cleaned_data["selling"],
                price=form.cleaned_data["price"],
                markup=form.cleaned_data["markup"],
                min_volume=form.cleaned_data["min_volume"],
                max_volume=form.cleaned_data["max_volume"],
            )
            ad_object.save()
            ad_object.refresh_from_db()
            return redirect('ad', ad_object.pk)
        else:
            # if form not valid, display it again with message
            messages.info(request, f'Form ain\'t valid my dear.')
            return render(request, 'webapp/new_ad.html', {'form': form})
    form = AdForm()
    return render(request, 'webapp/new_ad.html', {'form': form})

@login_required
def new_review(request, username):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # More validation to see if user can post review about the trader 
            # Hasn't posted too recently already
            # Has chatted to trader recently

            trader_object = get_object_or_404(User, username=username)

            # Add review to database
            review_object = Review(
                trader=trader_object,
                reviewer=request.user,
                review_title=form.cleaned_data["title"],
                comment=form.cleaned_data["comment"],
                score=form.cleaned_data["score"],
            )
            review_object.save()
            review_object.refresh_from_db()
            return redirect('detail', review_object.trader)
        else:
            # if form not valid, display it again with message
            return render(request, 'webapp/new_review.html', {'form': form})
    form = ReviewForm()
    return render(request, 'webapp/new_review.html', {'form': form})

def signup(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profile.phone_number = form.cleaned_data.get('phone_number')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.info(request, f'Welcome, {user}.')
            return redirect('index')
        else:
            # if form not valid, display it again with errors
            return render(request, 'webapp/signup.html', {'form': form})
    form = RegisterForm()
    return render(request, 'webapp/signup.html', {'form': form})

def login(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=raw_password)
            if user is not None:
                auth_login(request, user)
                messages.info(request, f'Welcome, {user}.')
                return redirect('index')
        else:
            # if form not valid, display it again with message
            messages.info(request, f'Username and password combination does not exist in our records')
            return render(request, 'webapp/login.html', {'form': form})
    form = AuthenticationForm()
    return render(request, 'webapp/login.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'webapp/profile.html')

@login_required
def edit_profile(request):
    user = request.user

    # Disable fields which have already been verified
    disabled_localbitcoins = user.profile.localbitcoins_verified
    disabled_paxful = user.profile.paxful_verified

    verification_code = get_verification_code(user.username)
    if request.method == 'POST':
        form = ImportReputationForm(user.profile.localbitcoins_username, user.profile.paxful_username, disabled_localbitcoins, disabled_paxful, request.POST)

        if form.is_valid():
            new_localbitcoins_username = form.cleaned_data.get('localbitcoins_username')
            new_paxful_username = form.cleaned_data.get('paxful_username')

            # Can only try verify account if it hasn't already been verified
            if user.profile.localbitcoins_verified == False:
                user.profile.localbitcoins_username = new_localbitcoins_username

                if new_localbitcoins_username == '':
                    user.profile.localbitcoins_request = False
                else:
                    if verfiy_localbitcoins(user.username, new_localbitcoins_username):
                        # Try automatically verify the user
                        user.profile.localbitcoins_verified = True
                        messages.info(request, f'LocalBitcoins verification successful!')
                    else:
                        # Flag up the user for manual checking
                        user.profile.localbitcoins_request = True
                        
                        messages.info(request, f'Automatic LocalBitcoins verification failed.')
                        messages.info(request, f'Your request has been raised and will be checked manually')
                        messages.info(request, f'If you are still having trouble, try contacting us. We respond very quickly!')
            
            # Can only try verify account if it hasn't already been verified
            if user.profile.paxful_verified == False:
                user.profile.paxful_username = new_paxful_username

                if new_paxful_username == '':
                    user.profile.paxful_request = False
                else:
                    # Flag up the user for manual checking
                    user.profile.paxful_request = True

            messages.info(request, f'Your details have been updated')       
            user.save()
            return render(request, 'webapp/edit_profile.html', {'form': form, 'verification_code': verification_code})

    form = ImportReputationForm(user.profile.localbitcoins_username, user.profile.paxful_username, disabled_localbitcoins, disabled_paxful)
    return render(request, 'webapp/edit_profile.html', {'form': form, 'verification_code': verification_code})

@login_required
def logout(request):
    auth_logout(request)
    messages.error(request, f'Logged out.')
    return redirect('index')

def get_locations(request):
    location = request.GET.get('location', None)
    
    predictions = get_google_autocomplete_locations(location, request.session)

    if predictions is None:
        data = {
            'locations': 'null'
        }
        return JsonResponse(data)
    else:
        data = {
            'locations': [{'value': i['description'], 'id': i['place_id']} for i in predictions]
        }
        return JsonResponse(data)
