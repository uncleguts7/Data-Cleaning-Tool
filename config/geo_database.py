"""Geographical database for city-country validation."""

CITY_COUNTRY_MAP = {
    # Egypt (مصر)
    'egypt': ['cairo', 'القاهرة', 'alexandria', 'الإسكندرية', 'giza', 'الجيزة', 'shubra el kheima', 'شبرا الخيمة', 'port said', 'بورسعيد', 'suez', 'السويس', 'luxor', 'الأقصر', 'mansoura', 'المنصورة', 'tanta', 'طنطا', 'asyut', 'أسيوط', 'ismailia', 'الإسماعيلية', 'fayyum', 'الفيوم', 'zagazig', 'الزقازيق', 'aswan', 'أسوان', 'damietta', 'دمياط', 'damanhur', 'دمنهور', 'minya', 'المنيا', 'beni suef', 'بني سويف', 'qena', 'قنا', 'sohag', 'سوهاج', 'hurghada', 'الغردقة', 'sharm el sheikh', 'شرم الشيخ', 'marsa alam', 'مرسى علم', 'dahab', 'دهب', 'el gouna', 'الجونة', 'kafr el sheikh', 'كفر الشيخ', 'shibin el kom', 'شبين الكوم', 'banha', 'بنها', 'arish', 'العريش'],
    'مصر': ['cairo', 'القاهرة', 'alexandria', 'الإسكندرية', 'giza', 'الجيزة', 'shubra el kheima', 'شبرا الخيمة', 'port said', 'بورسعيد'],
    
    # Saudi Arabia (السعودية)
    'saudi arabia': ['riyadh', 'الرياض', 'jeddah', 'جدة', 'mecca', 'مكة', 'مكة المكرمة', 'medina', 'المدينة', 'المدينة المنورة', 'dammam', 'الدمام', 'khobar', 'الخبر', 'dhahran', 'الظهران', 'tabuk', 'تبوك', 'buraydah', 'بريدة', 'khamis mushait', 'خميس مشيط', 'hail', 'حائل', 'najran', 'نجران', 'jazan', 'جازان', 'yanbu', 'ينبع', 'abha', 'أبها', 'qatif', 'القطيف', 'jubail', 'الجبيل', 'taif', 'الطائف', 'hafar al batin', 'حفر الباطن', 'sakaka', 'سكاكا', 'arar', 'عرعر', 'al kharj', 'الخرج', 'al ahsa', 'الأحساء', 'al qunfudhah', 'القنفذة', 'jizan', 'جيزان'],
    'السعودية': ['riyadh', 'الرياض', 'jeddah', 'جدة', 'mecca', 'مكة', 'medina', 'المدينة', 'dammam', 'الدمام'],
    'ksa': ['riyadh', 'jeddah', 'mecca', 'medina', 'dammam', 'khobar'],
    
    # UAE (الإمارات)
    'uae': ['dubai', 'دبي', 'abu dhabi', 'أبوظبي', 'أبو ظبي', 'sharjah', 'الشارقة', 'ajman', 'عجمان', 'ras al khaimah', 'رأس الخيمة', 'fujairah', 'الفجيرة', 'umm al quwain', 'أم القيوين', 'al ain', 'العين'],
    'united arab emirates': ['dubai', 'دبي', 'abu dhabi', 'أبوظبي', 'sharjah', 'الشارقة', 'ajman', 'عجمان', 'ras al khaimah', 'fujairah', 'al ain'],
    'الإمارات': ['dubai', 'دبي', 'abu dhabi', 'أبوظبي', 'sharjah', 'الشارقة', 'ajman', 'عجمان'],
    
    # Kuwait (الكويت)
    'kuwait': ['kuwait city', 'الكويت', 'hawalli', 'حولي', 'farwaniya', 'الفروانية', 'salmiya', 'السالمية', 'jahra', 'الجهراء', 'ahmadi', 'الأحمدي', 'fintas', 'الفنطاس', 'mahboula', 'المهبولة', 'fahaheel', 'الفحيحيل', 'mangaf', 'المنقف'],
    'الكويت': ['kuwait city', 'الكويت', 'hawalli', 'حولي', 'salmiya', 'السالمية'],
    
    # Qatar (قطر)
    'qatar': ['doha', 'الدوحة', 'al rayyan', 'الريان', 'al wakrah', 'الوكرة', 'al khor', 'الخور', 'dukhan', 'دخان', 'umm salal', 'أم صلال', 'lusail', 'لوسيل', 'mesaieed', 'مسيعيد'],
    'قطر': ['doha', 'الدوحة', 'al rayyan', 'الريان', 'al wakrah', 'الوكرة', 'lusail', 'لوسيل'],
    
    # Bahrain (البحرين)
    'bahrain': ['manama', 'المنامة', 'muharraq', 'المحرق', 'riffa', 'الرفاع', 'hamad town', 'مدينة حمد', 'isa town', 'مدينة عيسى', 'sitra', 'سترة', 'budaiya', 'البديع'],
    'البحرين': ['manama', 'المنامة', 'muharraq', 'المحرق', 'riffa', 'الرفاع'],
    
    # Oman (عمان)
    'oman': ['muscat', 'مسقط', 'salalah', 'صلالة', 'sohar', 'صحار', 'nizwa', 'نزوى', 'sur', 'صور', 'barka', 'بركاء', 'ibri', 'عبري', 'rustaq', 'الرستاق', 'buraimi', 'البريمي'],
    'عمان': ['muscat', 'مسقط', 'salalah', 'صلالة', 'sohar', 'صحار', 'nizwa', 'نزوى'],
    
    # Jordan (الأردن)
    'jordan': ['amman', 'عمان', 'zarqa', 'الزرقاء', 'irbid', 'إربد', 'aqaba', 'العقبة', 'madaba', 'مادبا', 'jerash', 'جرش', 'salt', 'السلط', 'karak', 'الكرك', 'mafraq', 'المفرق', 'tafilah', 'الطفيلة', 'petra', 'البتراء'],
    'الأردن': ['amman', 'عمان', 'zarqa', 'الزرقاء', 'irbid', 'إربد', 'aqaba', 'العقبة'],
    
    # Lebanon (لبنان)
    'lebanon': ['beirut', 'بيروت', 'tripoli', 'طرابلس', 'sidon', 'صيدا', 'tyre', 'صور', 'nabatieh', 'النبطية', 'zahle', 'زحلة', 'baalbek', 'بعلبك', 'jounieh', 'جونيه', 'byblos', 'جبيل'],
    'لبنان': ['beirut', 'بيروت', 'tripoli', 'طرابلس', 'sidon', 'صيدا', 'tyre', 'صور'],
    
    # Iraq (العراق)
    'iraq': ['baghdad', 'بغداد', 'basra', 'البصرة', 'mosul', 'الموصل', 'erbil', 'أربيل', 'kirkuk', 'كركوك', 'najaf', 'النجف', 'karbala', 'كربلاء', 'sulaymaniyah', 'السليمانية', 'nasiriyah', 'الناصرية', 'amarah', 'العمارة', 'diwaniyah', 'الديوانية', 'kut', 'الكوت', 'hillah', 'الحلة', 'ramadi', 'الرمادي', 'duhok', 'دهوك'],
    'العراق': ['baghdad', 'بغداد', 'basra', 'البصرة', 'mosul', 'الموصل', 'erbil', 'أربيل'],
    
    # Syria (سوريا)
    'syria': ['damascus', 'دمشق', 'aleppo', 'حلب', 'homs', 'حمص', 'latakia', 'اللاذقية', 'hama', 'حماة', 'deir ez-zor', 'دير الزور', 'raqqa', 'الرقة', 'daraa', 'درعا', 'tartus', 'طرطوس', 'idlib', 'إدلب'],
    'سوريا': ['damascus', 'دمشق', 'aleppo', 'حلب', 'homs', 'حمص', 'latakia', 'اللاذقية'],
    
    # Palestine (فلسطين)
    'palestine': ['jerusalem', 'القدس', 'gaza', 'غزة', 'ramallah', 'رام الله', 'hebron', 'الخليل', 'nablus', 'نابلس', 'jenin', 'جنين', 'bethlehem', 'بيت لحم', 'khan yunis', 'خان يونس', 'rafah', 'رفح', 'tulkarm', 'طولكرم', 'qalqilya', 'قلقيلية', 'jericho', 'أريحا'],
    'فلسطين': ['jerusalem', 'القدس', 'gaza', 'غزة', 'ramallah', 'رام الله', 'hebron', 'الخليل', 'nablus', 'نابلس'],
    
    # Morocco (المغرب)
    'morocco': ['casablanca', 'الدار البيضاء', 'rabat', 'الرباط', 'fes', 'فاس', 'marrakech', 'مراكش', 'tangier', 'طنجة', 'agadir', 'أكادير', 'meknes', 'مكناس', 'oujda', 'وجدة', 'kenitra', 'القنيطرة', 'tetouan', 'تطوان', 'safi', 'آسفي', 'mohammedia', 'المحمدية', 'khouribga', 'خريبكة', 'beni mellal', 'بني ملال', 'el jadida', 'الجديدة'],
    'المغرب': ['casablanca', 'الدار البيضاء', 'rabat', 'الرباط', 'fes', 'فاس', 'marrakech', 'مراكش'],
    
    # Algeria (الجزائر)
    'algeria': ['algiers', 'الجزائر', 'oran', 'وهران', 'constantine', 'قسنطينة', 'annaba', 'عنابة', 'blida', 'البليدة', 'batna', 'باتنة', 'setif', 'سطيف', 'tlemcen', 'تلمسان', 'biskra', 'بسكرة', 'tebessa', 'تبسة', 'bechar', 'بشار', 'tiaret', 'تيارت'],
    'الجزائر': ['algiers', 'الجزائر', 'oran', 'وهران', 'constantine', 'قسنطينة', 'annaba', 'عنابة'],
    
    # Tunisia (تونس)
    'tunisia': ['tunis', 'تونس', 'sfax', 'صفاقس', 'sousse', 'سوسة', 'kairouan', 'القيروان', 'bizerte', 'بنزرت', 'gabes', 'قابس', 'ariana', 'أريانة', 'gafsa', 'قفصة', 'monastir', 'المنستير', 'ben arous', 'بن عروس'],
    'تونس': ['tunis', 'تونس', 'sfax', 'صفاقس', 'sousse', 'سوسة', 'kairouan', 'القيروان'],
    
    # Libya (ليبيا)
    'libya': ['tripoli', 'طرابلس', 'benghazi', 'بنغازي', 'misrata', 'مصراتة', 'tarhuna', 'ترهونة', 'zawiya', 'الزاوية', 'tobruk', 'طبرق', 'ajdabiya', 'أجدابيا', 'Sabha', 'سبها'],
    'ليبيا': ['tripoli', 'طرابلس', 'benghazi', 'بنغازي', 'misrata', 'مصراتة'],
    
    # Sudan (السودان)
    'sudan': ['khartoum', 'الخرطوم', 'omdurman', 'أم درمان', 'port sudan', 'بورتسودان', 'kassala', 'كسلا', 'nyala', 'نيالا', 'el obeid', 'الأبيض', 'al qadarif', 'القضارف', 'wad madani', 'ود مدني', 'atbara', 'عطبرة'],
    'السودان': ['khartoum', 'الخرطوم', 'omdurman', 'أم درمان', 'port sudan', 'بورتسودان'],
    
    # Turkey (تركيا)
    'turkey': ['istanbul', 'إسطنبول', 'استانبول', 'ankara', 'أنقرة', 'izmir', 'إزمير', 'bursa', 'بورصة', 'adana', 'أضنة', 'gaziantep', 'غازي عنتاب', 'konya', 'قونية', 'antalya', 'أنطاليا', 'kayseri', 'قيصري', 'mersin', 'مرسين', 'eskisehir', 'إسكي شهير', 'diyarbakir', 'ديار بكر', 'samsun', 'سامسون', 'denizli', 'دنيزلي', 'trabzon', 'طرابزون', 'malatya', 'ملاطيا', 'kahramanmaras', 'قهرمان مرعش', 'van', 'فان', 'batman', 'باتمان', 'elazig', 'الازيغ', 'erzurum', 'أرضروم'],
    'تركيا': ['istanbul', 'إسطنبول', 'ankara', 'أنقرة', 'izmir', 'إزمير', 'bursa', 'بورصة', 'antalya', 'أنطاليا'],
    
    # USA (أمريكا)
    'usa': ['new york', 'نيويورك', 'los angeles', 'لوس أنجلوس', 'chicago', 'شيكاغو', 'houston', 'هيوستن', 'phoenix', 'فينيكس', 'philadelphia', 'فيلادلفيا', 'san antonio', 'سان أنطونيو', 'san diego', 'سان دييغو', 'dallas', 'دالاس', 'san jose', 'سان خوسيه', 'austin', 'أوستن', 'jacksonville', 'جاكسونفيل', 'fort worth', 'فورت وورث', 'columbus', 'كولومبوس', 'charlotte', 'شارلوت', 'san francisco', 'سان فرانسيسكو', 'indianapolis', 'إنديانابوليس', 'seattle', 'سياتل', 'denver', 'دنفر', 'washington', 'واشنطن', 'boston', 'بوسطن', 'detroit', 'ديترويت', 'nashville', 'ناشفيل', 'memphis', 'ممفيس', 'portland', 'بورتلاند', 'las vegas', 'لاس فيغاس', 'baltimore', 'بالتيمور', 'milwaukee', 'ميلووكي', 'atlanta', 'أتلانتا', 'miami', 'ميامي', 'orlando', 'أورلاندو', 'tampa', 'تامبا', 'minneapolis', 'مينيابوليس'],
    'united states': ['new york', 'los angeles', 'chicago', 'houston', 'phoenix', 'philadelphia', 'san antonio', 'san diego', 'dallas', 'san jose', 'austin', 'washington', 'boston', 'miami'],
    'america': ['new york', 'los angeles', 'chicago', 'houston', 'miami', 'san francisco', 'seattle', 'boston', 'las vegas'],
    'أمريكا': ['new york', 'نيويورك', 'los angeles', 'لوس أنجلوس', 'chicago', 'شيكاغو', 'miami', 'ميامي'],
    
    # UK (بريطانيا)
    'uk': ['london', 'لندن', 'birmingham', 'برمنغهام', 'manchester', 'مانشستر', 'liverpool', 'ليفربول', 'leeds', 'ليدز', 'glasgow', 'غلاسكو', 'edinburgh', 'إدنبرة', 'bristol', 'بريستول', 'cardiff', 'كارديف', 'belfast', 'بلفاست', 'sheffield', 'شيفيلد', 'newcastle', 'نيوكاسل', 'nottingham', 'نوتنغهام', 'leicester', 'ليستر', 'southampton', 'ساوثهامبتون', 'oxford', 'أكسفورد', 'cambridge', 'كامبريدج', 'coventry', 'كوفنتري', 'brighton', 'برايتون'],
    'united kingdom': ['london', 'birmingham', 'manchester', 'liverpool', 'leeds', 'glasgow', 'edinburgh', 'bristol', 'cardiff', 'belfast'],
    'britain': ['london', 'manchester', 'liverpool', 'birmingham', 'edinburgh', 'glasgow'],
    'بريطانيا': ['london', 'لندن', 'manchester', 'مانشستر', 'liverpool', 'ليفربول'],
    
    # Germany (ألمانيا)
    'germany': ['berlin', 'برلين', 'hamburg', 'هامبورغ', 'munich', 'ميونخ', 'cologne', 'كولونيا', 'frankfurt', 'فرانكفورت', 'stuttgart', 'شتوتغارت', 'dusseldorf', 'دوسلدورف', 'dortmund', 'دورتموند', 'essen', 'إيسن', 'leipzig', 'لايبزيغ', 'bremen', 'بريمن', 'dresden', 'دريسدن', 'hannover', 'هانوفر', 'nuremberg', 'نورمبرغ'],
    'ألمانيا': ['berlin', 'برلين', 'munich', 'ميونخ', 'hamburg', 'هامبورغ', 'cologne', 'كولونيا'],
    
    # France (فرنسا)
    'france': ['paris', 'باريس', 'marseille', 'مرسيليا', 'lyon', 'ليون', 'toulouse', 'تولوز', 'nice', 'نيس', 'nantes', 'نانت', 'strasbourg', 'ستراسبورغ', 'montpellier', 'مونبلييه', 'bordeaux', 'بوردو', 'lille', 'ليل', 'rennes', 'رين', 'reims', 'ريمس'],
    'فرنسا': ['paris', 'باريس', 'marseille', 'مرسيليا', 'lyon', 'ليون', 'nice', 'نيس'],
    
    # Italy (إيطاليا)
    'italy': ['rome', 'روما', 'milan', 'ميلان', 'naples', 'نابولي', 'turin', 'تورينو', 'palermo', 'باليرمو', 'genoa', 'جنوة', 'bologna', 'بولونيا', 'florence', 'فلورنسا', 'venice', 'البندقية', 'verona', 'فيرونا', 'catania', 'كاتانيا'],
    'إيطاليا': ['rome', 'روما', 'milan', 'ميلان', 'naples', 'نابولي', 'venice', 'البندقية'],
    
    # Spain (إسبانيا)
    'spain': ['madrid', 'مدريد', 'barcelona', 'برشلونة', 'valencia', 'فالنسيا', 'seville', 'إشبيلية', 'zaragoza', 'سرقسطة', 'malaga', 'مالقة', 'murcia', 'مرسية', 'palma', 'بالما', 'bilbao', 'بلباو', 'alicante', 'أليكانتي'],
    'إسبانيا': ['madrid', 'مدريد', 'barcelona', 'برشلونة', 'valencia', 'فالنسيا', 'seville', 'إشبيلية'],
    
    # China (الصين)
    'china': ['beijing', 'بكين', 'shanghai', 'شنغهاي', 'guangzhou', 'قوانغتشو', 'shenzhen', 'شنتشن', 'chengdu', 'تشنغدو', 'wuhan', 'ووهان', 'xian', 'شيان', 'hangzhou', 'هانغتشو', 'nanjing', 'نانجينغ', 'tianjin', 'تيانجين', 'chongqing', 'تشونغتشينغ', 'suzhou', 'سوتشو', 'dongguan', 'دونغقوان', 'shenyang', 'شنيانغ', 'harbin', 'هاربين', 'qingdao', 'تشينغداو'],
    'الصين': ['beijing', 'بكين', 'shanghai', 'شنغهاي', 'guangzhou', 'قوانغتشو', 'shenzhen', 'شنتشن'],
    
    # Japan (اليابان)
    'japan': ['tokyo', 'طوكيو', 'yokohama', 'يوكوهاما', 'osaka', 'أوساكا', 'nagoya', 'ناغويا', 'sapporo', 'سابورو', 'fukuoka', 'فوكوكا', 'kobe', 'كوبي', 'kyoto', 'كيوتو', 'kawasaki', 'كاواساكي', 'saitama', 'سايتاما', 'hiroshima', 'هيروشيما'],
    'اليابان': ['tokyo', 'طوكيو', 'osaka', 'أوساكا', 'kyoto', 'كيوتو', 'yokohama', 'يوكوهاما'],
    
    # South Korea (كوريا الجنوبية)
    'south korea': ['seoul', 'سيول', 'busan', 'بوسان', 'incheon', 'إنتشون', 'daegu', 'دايغو', 'daejeon', 'دايجون', 'gwangju', 'غوانغجو', 'suwon', 'سووون', 'ulsan', 'أولسان'],
    'korea': ['seoul', 'busan', 'incheon', 'daegu', 'daejeon'],
    'كوريا': ['seoul', 'سيول', 'busan', 'بوسان'],
    
    # India (الهند)
    'india': ['mumbai', 'مومباي', 'delhi', 'دلهي', 'bangalore', 'بنغالور', 'hyderabad', 'حيدر أباد', 'chennai', 'تشيناي', 'kolkata', 'كولكاتا', 'pune', 'بونه', 'ahmedabad', 'أحمد آباد', 'jaipur', 'جايبور', 'lucknow', 'لكناو', 'kanpur', 'كانبور', 'nagpur', 'ناغبور', 'indore', 'إندور', 'bhopal', 'بوبال', 'visakhapatnam', 'فيساكاباتنام'],
    'الهند': ['mumbai', 'مومباي', 'delhi', 'دلهي', 'bangalore', 'بنغالور', 'chennai', 'تشيناي'],
    
    # Pakistan (باكستان)
    'pakistan': ['karachi', 'كراتشي', 'lahore', 'لاهور', 'islamabad', 'إسلام أباد', 'rawalpindi', 'راولبندي', 'faisalabad', 'فيصل آباد', 'multan', 'ملتان', 'peshawar', 'بيشاور', 'quetta', 'كويتا', 'sialkot', 'سيالكوت', 'gujranwala', 'غوجرانوالا'],
    'باكستان': ['karachi', 'كراتشي', 'lahore', 'لاهور', 'islamabad', 'إسلام أباد'],
    
    # Bangladesh (بنغلاديش)
    'bangladesh': ['dhaka', 'دكا', 'chittagong', 'شيتاغونغ', 'khulna', 'خولنا', 'rajshahi', 'راجشاهي', 'sylhet', 'سيلهت', 'barisal', 'باريسال'],
    'بنغلاديش': ['dhaka', 'دكا', 'chittagong', 'شيتاغونغ'],
    
    # Indonesia (إندونيسيا)
    'indonesia': ['jakarta', 'جاكرتا', 'surabaya', 'سورابايا', 'bandung', 'باندونغ', 'medan', 'ميدان', 'semarang', 'سيمارانج', 'makassar', 'ماكاسار', 'palembang', 'باليمبانغ', 'denpasar', 'دينباسار', 'yogyakarta', 'يوجياكارتا'],
    'إندونيسيا': ['jakarta', 'جاكرتا', 'surabaya', 'سورابايا', 'bandung', 'باندونغ'],
    
    # Malaysia (ماليزيا)
    'malaysia': ['kuala lumpur', 'كوالالمبور', 'george town', 'جورج تاون', 'ipoh', 'إيبوه', 'johor bahru', 'جوهور بهرو', 'malacca', 'ملقا', 'kota kinabalu', 'كوتا كينابالو', 'kuching', 'كوتشينغ'],
    'ماليزيا': ['kuala lumpur', 'كوالالمبور', 'george town', 'جورج تاون', 'johor bahru', 'جوهور بهرو'],
    
    # Singapore (سنغافورة)
    'singapore': ['singapore', 'سنغافورة'],
    'سنغافورة': ['singapore', 'سنغافورة'],
    
    # Thailand (تايلاند)
    'thailand': ['bangkok', 'بانكوك', 'chiang mai', 'شيانغ ماي', 'pattaya', 'باتايا', 'phuket', 'بوكيت', 'hat yai', 'هات ياي', 'nakhon ratchasima', 'ناخون راتشاسيما'],
    'تايلاند': ['bangkok', 'بانكوك', 'phuket', 'بوكيت', 'pattaya', 'باتايا'],
    
    # Canada (كندا)
    'canada': ['toronto', 'تورونتو', 'montreal', 'مونتريال', 'vancouver', 'فانكوفر', 'calgary', 'كالغاري', 'ottawa', 'أوتاوا', 'edmonton', 'إدمونتون', 'winnipeg', 'وينيبيغ', 'quebec city', 'كيبيك', 'hamilton', 'هاميلتون', 'kitchener', 'كيتشنر'],
    'كندا': ['toronto', 'تورونتو', 'montreal', 'مونتريال', 'vancouver', 'فانكوفر', 'ottawa', 'أوتاوا'],
    
    # Australia (أستراليا)
    'australia': ['sydney', 'سيدني', 'melbourne', 'ملبورن', 'brisbane', 'بريزبن', 'perth', 'بيرث', 'adelaide', 'أديليد', 'gold coast', 'الساحل الذهبي', 'newcastle', 'نيوكاسل', 'canberra', 'كانبيرا', 'sunshine coast', 'ساحل الشمس', 'hobart', 'هوبارت'],
    'أستراليا': ['sydney', 'سيدني', 'melbourne', 'ملبورن', 'brisbane', 'بريزبن', 'perth', 'بيرث'],
    
    # Brazil (البرازيل)
    'brazil': ['sao paulo', 'ساو باولو', 'rio de janeiro', 'ريو دي جانيرو', 'brasilia', 'برازيليا', 'salvador', 'سلفادور', 'fortaleza', 'فورتاليزا', 'belo horizonte', 'بيلو هوريزونتي', 'manaus', 'ماناوس', 'curitiba', 'كوريتيبا', 'recife', 'ريسيفي'],
    'البرازيل': ['sao paulo', 'ساو باولو', 'rio de janeiro', 'ريو دي جانيرو', 'brasilia', 'برازيليا'],
    
    # Russia (روسيا)
    'russia': ['moscow', 'موسكو', 'saint petersburg', 'سانت بطرسبرغ', 'novosibirsk', 'نوفوسيبيرسك', 'yekaterinburg', 'يكاترينبورغ', 'kazan', 'قازان', 'nizhny novgorod', 'نيجني نوفغورود', 'chelyabinsk', 'تشيليابينسك', 'samara', 'سامارا', 'omsk', 'أومسك', 'rostov-on-don', 'روستوف'],
    'روسيا': ['moscow', 'موسكو', 'saint petersburg', 'سانت بطرسبرغ', 'kazan', 'قازان'],
    
    # Mexico (المكسيك)
    'mexico': ['mexico city', 'مكسيكو سيتي', 'guadalajara', 'غوادالاخارا', 'monterrey', 'مونتيري', 'puebla', 'بويبلا', 'tijuana', 'تيخوانا', 'cancun', 'كانكون', 'leon', 'ليون', 'juarez', 'خواريز'],
    'المكسيك': ['mexico city', 'مكسيكو سيتي', 'cancun', 'كانكون', 'guadalajara', 'غوادالاخارا'],
    
    # Argentina (الأرجنتين)
    'argentina': ['buenos aires', 'بوينس آيرس', 'cordoba', 'قرطبة', 'rosario', 'روساريو', 'mendoza', 'ميندوزا', 'la plata', 'لا بلاتا', 'mar del plata', 'مار دل بلاتا'],
    'الأرجنتين': ['buenos aires', 'بوينس آيرس', 'cordoba', 'قرطبة'],
    
    # South Africa (جنوب أفريقيا)
    'south africa': ['johannesburg', 'جوهانسبرغ', 'cape town', 'كيب تاون', 'durban', 'ديربان', 'pretoria', 'بريتوريا', 'port elizabeth', 'بورت إليزابيث', 'bloemfontein', 'بلومفونتين'],
    'جنوب أفريقيا': ['johannesburg', 'جوهانسبرغ', 'cape town', 'كيب تاون', 'durban', 'ديربان'],
    
    # Nigeria (نيجيريا)
    'nigeria': ['lagos', 'لاغوس', 'kano', 'كانو', 'ibadan', 'إبادان', 'abuja', 'أبوجا', 'port harcourt', 'بورت هاركورت', 'benin city', 'بنين سيتي'],
    'نيجيريا': ['lagos', 'لاغوس', 'abuja', 'أبوجا', 'kano', 'كانو'],
    
    # Kenya (كينيا)
    'kenya': ['nairobi', 'نيروبي', 'mombasa', 'مومباسا', 'kisumu', 'كيسومو', 'nakuru', 'ناكورو', 'eldoret', 'إلدوريت'],
    'كينيا': ['nairobi', 'نيروبي', 'mombasa', 'مومباسا'],
    
    # Ethiopia (إثيوبيا)
    'ethiopia': ['addis ababa', 'أديس أبابا', 'dire dawa', 'ديري داوا', 'mekelle', 'ميكيلي', 'gondar', 'غوندار', 'bahir dar', 'بحر دار'],
    'إثيوبيا': ['addis ababa', 'أديس أبابا', 'dire dawa', 'ديري داوا'],
    
    # Iran (إيران)
    'iran': ['tehran', 'طهران', 'mashhad', 'مشهد', 'isfahan', 'أصفهان', 'karaj', 'كرج', 'tabriz', 'تبريز', 'shiraz', 'شيراز', 'qom', 'قم', 'ahvaz', 'الأهواز', 'kermanshah', 'كرمنشاه'],
    'إيران': ['tehran', 'طهران', 'mashhad', 'مشهد', 'isfahan', 'أصفهان', 'shiraz', 'شيراز'],
    
    # Yemen (اليمن)
    'yemen': ['sanaa', 'صنعاء', 'aden', 'عدن', 'taiz', 'تعز', 'hodeidah', 'الحديدة', 'ibb', 'إب', 'dhamar', 'ذمار', 'mukalla', 'المكلا'],
    'اليمن': ['sanaa', 'صنعاء', 'aden', 'عدن', 'taiz', 'تعز', 'hodeidah', 'الحديدة'],
}