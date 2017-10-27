from django.shortcuts import render
from django.utils import timezone
from .models import Log
from datetime import datetime, timedelta
from django.http import HttpResponse


def get_temp_humi(raw_temp_data, raw_humi_data):
    if (raw_temp_data >= 0):
        if (raw_temp_data < 22):
            temp = 22 - raw_temp_data;
        else:
            temp = raw_temp_data - 22;
        temp *= (20.0 / 3);
        temp = 100 - temp;
        measurement_temp_data = temp;
    else:
        measurement_temp_data = 0;

    if (raw_humi_data >= 0):
        if (raw_humi_data < 50):
            temp = 50 - raw_humi_data;
        else:
            temp = raw_humi_data - 50;
        temp *= (20.0 / 10);
        temp = 100 - temp;
        measurement_humi_data = temp;
    else:
        measurement_humi_data = 0;

    if (measurement_humi_data < 0):
        measurement_humi_data = 0;
    if (measurement_temp_data < 0):
        measurement_temp_data = 0;

    return measurement_temp_data, measurement_humi_data;

def get_gas(raw_co2_data):
    temp = raw_co2_data;

    if (raw_co2_data <= 700):
        temp *= (20.0 / 700);
        measurement_co2_data = 100 - temp;
    elif (raw_co2_data <= 1000):
        temp -= 700;
        temp *= (20.0 / 300);
        measurement_co2_data = 80 - temp;
    elif (raw_co2_data <= 2000):
        temp -= 1000;
        temp *= (20.0 / 1000);
        measurement_co2_data = 60 - temp;
    elif (raw_co2_data <= 3000):
        temp -= 2000;
        temp *= (40.0 / 1000);
        measurement_co2_data = 40 - temp;
    else:
        measurement_co2_data = 0;

    return measurement_co2_data

def get_dust(raw_dust_data):
    dust_temp = raw_dust_data;

    if (raw_dust_data <= 0):
        measurement_dust_data = 100;
    elif (raw_dust_data <= 30):
        dust_temp *= (20.0 / 30);
        measurement_dust_data = 100 - dust_temp;
    elif (raw_dust_data <= 80):
        dust_temp -= 30;
        dust_temp *= (20.0 / 50);
        measurement_dust_data = 80 - dust_temp;
    elif (raw_dust_data <= 150):
        dust_temp -= 80;
        dust_temp *= (20.0 / 70);
        measurement_dust_data = 60 - dust_temp;
    elif (raw_dust_data <= 240):
        dust_temp -= 150;
        dust_temp *= (40.0 / 90);
        measurement_dust_data = 40 - dust_temp;
    else:
        measurement_dust_data = 0;

    return measurement_dust_data


def get_status(temperature, humidity, dust, gas):
    measurement_temp_data, measurement_humi_data = get_temp_humi(temperature, humidity)
    measurement_dust_data = get_dust(dust);
    measurement_co2_data = get_gas(gas);
    measurement_all_data = measurement_temp_data * 0.25;
    measurement_all_data += measurement_humi_data * 0.25;
    measurement_all_data += measurement_dust_data * 0.25;
    measurement_all_data += measurement_co2_data * 0.25;
    if (measurement_all_data <= 40):
        total_status = "양호";
        status_info = "실내 공기질 상태가 매우 양호합니다."
    elif (measurement_all_data <= 60):
        total_status = "보통";
        status_info = "현재 적정 수준의 상태이나 환기를 한번씩 해줄 필요가 있습니다.";
    elif (measurement_all_data <= 80):
        total_status = "주의";
        status_info = "실내 공기상태가 안좋습니다. 컨티션에 악영향을 미치고 있습니다. 빠른 시일 내 환기를 해주세요.";
    elif (measurement_all_data <= 100):
        total_status = "위험";
        status_info = "상태가 매우 안좋습니다. 지금 바로 환기를 해주세요.";

    return total_status, status_info


def set_data(request):
    device = request.GET.get("sn")
    temperature = request.GET.get("t")
    humidity = request.GET.get("h")
    dust = request.GET.get("d")
    gas = request.GET.get("c")

    Log.objects.create(device=device, temperature=temperature, humidity=humidity, dust=dust, gas=gas)

    return HttpResponse("입력성공!")

def post_list(request):
    posts = Log.objects.all().order_by('created_date')
    
    #현 시각으로 부터 1분 사이의 각 센서의 평균값을 구함.
    rpost = Log.objects.filter(created_date__gte=( timezone.datetime.now() - timedelta(minutes=1) ) )
    rpost_size = len(rpost)
    print('rpost:',len(rpost))
    if (rpost_size == 0):
        rpost_size = 1
    temperature = sum([post.temperature for post in rpost]) / rpost_size
    humidity = sum([post.humidity for post in rpost]) / rpost_size
    dust = sum([post.dust for post in rpost]) / rpost_size
    gas = sum([post.gas for post in rpost]) / rpost_size

    #상태 평가하기
    total_status, status_info = get_status(temperature, humidity, dust, gas)

    return render(
        request, 
        'blog/post_list.html',
         {
             'posts': posts,
             'total_status': total_status,
             'status_info': status_info,
             'temperature': temperature,
             'humidity': humidity,
             'dust': dust,
             'gas': gas
        }
    )
    