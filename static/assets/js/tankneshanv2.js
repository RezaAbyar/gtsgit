// توابع جدید اضافه شده
function getRealisticTruckTime(carDurationMinutes, distanceKm) {
    const carAvgSpeed = 80;
    const truckAvgSpeed = 50;

    const realisticTruckMinutes = Math.round((distanceKm / truckAvgSpeed) * 60);
    const additionalStopsTime = Math.round(realisticTruckMinutes * 0.1);

    return realisticTruckMinutes + additionalStopsTime;
}

function calculateTimeFromMinutes(departureTime, minutesToAdd) {
    const [depHour, depMinute] = departureTime.split(':').map(Number);
    const departureTotalMinutes = depHour * 60 + depMinute;
    const arrivalTotalMinutes = departureTotalMinutes + minutesToAdd;

    const arrivalHour = Math.floor(arrivalTotalMinutes / 60) % 24;
    const arrivalMinute = arrivalTotalMinutes % 60;

    return `${arrivalHour.toString().padStart(2, '0')}:${arrivalMinute.toString().padStart(2, '0')}`;
}

function calculateArrivalTime(durationText, departureTime, isTruck = false, distanceKm = null) {
    const persianToEnglish = (str) => {
        const persianNumbers = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
        const englishNumbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];

        return str.split('').map(char => {
            const index = persianNumbers.indexOf(char);
            return index !== -1 ? englishNumbers[index] : char;
        }).join('');
    };

    const englishDuration = persianToEnglish(durationText);

    let minutes = 0;

    if (englishDuration.includes('ساعت') || englishDuration.includes('hour')) {
        const hourMatch = englishDuration.match(/(\d+)\s*(ساعت|hour)/);
        const minuteMatch = englishDuration.match(/(\d+)\s*(دقیقه|minute)/);

        const hours = hourMatch ? parseInt(hourMatch[1]) : 0;
        const mins = minuteMatch ? parseInt(minuteMatch[1]) : 0;
        minutes = hours * 60 + mins;
    } else {
        const minuteMatch = englishDuration.match(/(\d+)/);
        minutes = minuteMatch ? parseInt(minuteMatch[1]) : 0;
    }

    // اصلاح زمان برای تریلی
    if (isTruck && distanceKm !== null) {
        if (minutes < 25) {
  minutes = Math.ceil(minutes * 2);
        } else {
            minutes = Math.ceil(minutes * 1.3);

        }
    }

    const [depHour, depMinute] = departureTime.split(':').map(Number);
    const departureTotalMinutes = depHour * 60 + depMinute;
    const arrivalTotalMinutes = departureTotalMinutes + minutes;

    const arrivalHour = Math.floor(arrivalTotalMinutes / 60) % 24;
    const arrivalMinute = arrivalTotalMinutes % 60;

    const formattedArrival = `${arrivalHour.toString().padStart(2, '0')}:${arrivalMinute.toString().padStart(2, '0')}`;

    return {
        minutesUntilArrival: minutes,
        arrivalTime: formattedArrival
    };
}

// تابع اصلی tankPosition (فقط بخش done تغییر کرده)
function tankPosition(sender, destinations, time) {
    waiting();

    if (!sender || sender.trim() === '' || sender === 'None') {
        ending();
        alert('🚚 برای مشاهده موقعیت نفتکش، مختصات جغرافیایی انبار مبدا باید در سیستم ثبت شده باشد.');
        return;
    }

    if (!destinations || destinations.trim() === '' || destinations === 'None') {
        ending();
        alert('🚚 برای مشاهده موقعیت نفتکش، مختصات جغرافیایی جایگاه مقصد باید در سیستم ثبت شده باشد.');
        return;
    }

    $.ajax({
        type: 'GET',
        dataType: "json",
        url: "https://api.neshan.org/v1/distance-matrix?type=car&origins=" + sender + "&destinations=" + destinations,
        headers: {"Api-Key": "service.cb6e1f04610d4f33b3e2f22e2e55061b"},
    }).done(function (data) {
        const durationText = data.rows[0].elements[0].duration.text;
        let distanceText = data.rows[0].elements[0].distance.text;
         const persianToEnglishNumbers = (str) => {
        const persianNumbers = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
        const englishNumbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];

        return str.split('').map(char => {
            const index = persianNumbers.indexOf(char);
            return index !== -1 ? englishNumbers[index] : char;
        }).join('');
    };
        let distanceKm;
        distanceText=persianToEnglishNumbers(distanceText)
        if (distanceText.includes('کیلومتر')) {
            distanceKm = parseFloat(distanceText.replace('کیلومتر', '').trim());
        } else if (distanceText.includes('km')) {
            distanceKm = parseFloat(distanceText.replace('km', '').trim());
        } else if (distanceText.includes('متر')) {
            distanceKm = parseFloat(distanceText.replace('متر', '').trim()) / 1000;
        } else if (distanceText.includes('m')) {
            distanceKm = parseFloat(distanceText.replace('m', '').trim()) / 1000;
        } else {
            distanceKm = 10; // پیش‌فرض
        }

        // استخراج مسافت به کیلومتر



    // محاسبه زمان رسیدن با در نظر گرفتن تریلی
    const arrivalInfo = calculateArrivalTime(durationText, time, true, distanceKm);

    createTrackingPanel(sender, destinations, arrivalInfo, distanceText, time);

    ending();
});
    }



// تابع ایجاد پنل ردیابی
function createTrackingPanel(sender, destination, arrivalInfo, distanceText, departureTime) {
    // حذف پنل قبلی اگر وجود دارد
    const existingPanel = document.getElementById('tankTrackingPanel');
    if (existingPanel) {
        existingPanel.remove();
    }

    // ایجاد پنل
    const panel = document.createElement('div');
    panel.id = 'tankTrackingPanel';
    panel.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 90%;
        max-width: 600px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        z-index: 10000;
        font-family: Tahoma;
        direction: rtl;
        overflow: hidden;
    `;

    // هدر پنل
    panel.innerHTML = `
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center;">
            <h3 style="margin: 0; font-size: 18px;">🚚 ردیابی موقعیت نفتکش</h3>
            <button onclick="closeTrackingPanel()" style="position: absolute; left: 15px; top: 15px; background: none; border: none; color: white; font-size: 20px; cursor: pointer;">×</button>
        </div>
        
        <div style="padding: 20px;">
            <!-- اطلاعات سفر -->
            <div style="display: flex; justify-content: space-between; margin-bottom: 20px; background: #f8f9fa; padding: 15px; border-radius: 10px;">
                <div style="text-align: center;">
                    <div style="font-size: 12px; color: #666;">مدت زمان</div>
                    <div style="font-size: 16px; font-weight: bold; color: #333;">${arrivalInfo.minutesUntilArrival} دقیقه</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 12px; color: #666;">مسافت</div>
                    <div style="font-size: 16px; font-weight: bold; color: #333;">${distanceText}</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 12px; color: #666;">زمان رسیدن</div>
                    <div style="font-size: 16px; font-weight: bold; color: #333;">${arrivalInfo.arrivalTime}</div>
                </div>
            </div>

            <!-- نقشه مسیر -->
            <div style="margin: 20px 0;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                    <!-- انبار (چپ) -->
                    <div style="display: flex; align-items: center;">
                        <div style="width: 40px; height: 40px; background: #4CAF50; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 18px;">🏭</div>
                        <div style="margin-right: 10px;">
                            <div style="font-size: 12px; color: #666;">مبدا</div>
                            <div style="font-size: 14px; font-weight: bold;">انبار</div>
                        </div>
                    </div>
                    
                    <!-- جایگاه (راست) -->
                    <div style="display: flex; align-items: center;">
                        <div style="width: 40px; height: 40px; background: #FF5722; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 18px;">⛽</div>
                        <div style="margin-right: 10px;">
                            <div style="font-size: 12px; color: #666;">مقصد</div>
                            <div style="font-size: 14px; font-weight: bold;">جایگاه</div>
                        </div>
                    </div>
                </div>

                <!-- خط مسیر -->
                <div style="position: relative; height: 4px; background: #e0e0e0; border-radius: 2px; margin: 20px 0;">
                    <div id="tankProgress" style="position: absolute; height: 100%; background: linear-gradient(90deg, #4CAF50, #FF9800, #FF5722); border-radius: 2px; width: 0%; transition: width 2s ease-in-out;"></div>
                    
                    <!-- موقعیت نفتکش -->
                    <div id="tankIcon" style="position: absolute; top: 50%; transform: translate(-50%, -50%); font-size: 24px; transition: left 2s ease-in-out; right: 0%;">
                        🚛
                    </div>
                </div>

                <!-- وضعیت پیشرفت -->
                <div style="text-align: center; margin-top: 30px;">
                    <div id="progressText" style="font-size: 14px; color: #666;">در حال حرکت...</div>
                    <div id="progressPercent" style="font-size: 16px; font-weight: bold; color: #333;">0%</div>
                    <div id="timeInfo" style="font-size: 12px; color: #888; margin-top: 5px;"></div>
                </div>
            </div>

            <!-- دکمه بستن -->
            <button onclick="closeTrackingPanel()" style="width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; margin-top: 10px;">
                بستن
            </button>
        </div>
    `;

    document.body.appendChild(panel);

    // شبیه‌سازی حرکت نفتکش بر اساس زمان واقعی
    simulateTankMovementRealTime(departureTime, arrivalInfo.arrivalTime, arrivalInfo.minutesUntilArrival);
}

// تابع شبیه‌سازی حرکت نفتکش بر اساس زمان واقعی
function simulateTankMovementRealTime(departureTime, arrivalTime, totalMinutes) {
    const progressBar = document.getElementById('tankProgress');
    const tankIcon = document.getElementById('tankIcon');
    const progressText = document.getElementById('progressText');
    const progressPercent = document.getElementById('progressPercent');
    const timeInfo = document.getElementById('timeInfo');

    // تبدیل زمان‌ها به دقیقه
    const [depHour, depMinute] = departureTime.split(':').map(Number);
    const [arrHour, arrMinute] = arrivalTime.split(':').map(Number);

    const departureTotalMinutes = depHour * 60 + depMinute;
    const arrivalTotalMinutes = arrHour * 60 + arrMinute;

    // زمان فعلی
    const now = new Date();
    const currentHour = now.getHours();
    const currentMinute = now.getMinutes();
    const currentTotalMinutes = currentHour * 60 + currentMinute;

    // محاسبه پیشرفت واقعی
    let progress = 0;
    console.log((currentTotalMinutes >= arrivalTotalMinutes))
    console.log((currentTotalMinutes))
    console.log((arrivalTotalMinutes))
    if (currentTotalMinutes >= arrivalTotalMinutes) {
        // نفتکش به مقصد رسیده
        progress = 100;
    } else if (currentTotalMinutes <= departureTotalMinutes) {
        // نفتکش هنوز حرکت نکرده
        progress = 0;
    } else {
        // نفتکش در حال حرکت است
        const elapsedMinutes = currentTotalMinutes - departureTotalMinutes;
        progress = (elapsedMinutes / totalMinutes) * 100;
        progress = Math.min(Math.max(progress, 0), 100);
    }

    // اعمال پیشرفت (حرکت از چپ به راست)
    progressBar.style.width = progress + '%';
    tankIcon.style.right = progress + '%'; // حرکت از چپ به راست
    progressPercent.textContent = Math.round(progress) + '%';

    // به روز رسانی وضعیت متن
    updateProgressStatus(progress, progressText, timeInfo, departureTime, arrivalTime);

    // اگر سفر تمام نشده، هر 30 ثانیه به روز رسانی کن
    if (progress < 100) {
        setTimeout(() => {
            simulateTankMovementRealTime(departureTime, arrivalTime, totalMinutes);
        }, 30000);
    }
}

// تابع به روز رسانی وضعیت
function updateProgressStatus(progress, progressText, timeInfo, departureTime, arrivalTime) {
    if (progress === 0) {
        progressText.textContent = 'آماده حرکت از انبار';
        progressText.style.color = '#666';
        timeInfo.textContent = `زمان حرکت: ${departureTime}`;
    } else if (progress < 30) {
        progressText.textContent = 'در حال حرکت از انبار...';
        progressText.style.color = '#4CAF50';
        timeInfo.textContent = `مسیر ابتدایی`;
    } else if (progress < 70) {
        progressText.textContent = 'در میانه مسیر...';
        progressText.style.color = '#FF9800';
        timeInfo.textContent = `نیمه راه`;
    } else if (progress < 100) {
        progressText.textContent = 'نزدیک به مقصد...';
        progressText.style.color = '#FF5722';

        // محاسبه دقیقه‌های باقیمانده
        const remainingProgress = 100 - progress;
        const estimatedMinutesLeft = Math.round(remainingProgress / 2); // تقریب
        timeInfo.textContent = `حدود ${estimatedMinutesLeft} دقیقه دیگر`;
    } else {
        progressText.textContent = 'نفتکش به مقصد رسید';
        progressText.style.color = '#4CAF50';
        timeInfo.textContent = `در جایگاه مقصد`;
    }
}

// تابع بستن پنل
function closeTrackingPanel() {
    const panel = document.getElementById('tankTrackingPanel');
    const backdrop = document.getElementById('tankTrackingBackdrop');

    if (panel) {
        panel.remove();
    }
    if (backdrop) {
        backdrop.remove();
    }
}

// اضافه کردن backdrop برای پنل
function createBackdrop() {
    const backdrop = document.createElement('div');
    backdrop.id = 'tankTrackingBackdrop';
    backdrop.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        z-index: 9999;
    `;
    backdrop.onclick = closeTrackingPanel;
    document.body.appendChild(backdrop);
}

// اصلاح تابع tankPosition برای اضافه کردن backdrop
const originalTankPosition = tankPosition;
tankPosition = function (sender, destinations, time) {
    createBackdrop();
    originalTankPosition(sender, destinations, time);
};