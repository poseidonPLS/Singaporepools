
const TRANSLATIONS = {
    en: {
        // Nav
        "nav.dashboard": "Home",
        "nav.analysis": "Analysis",
        "nav.history": "History",
        "nav.settings": "Settings",
        "nav.donate": "Donate",

        // Hero
        "hero.title": "Predict Your <span class='hero__title-gradient'>Lucky Numbers</span>",
        "hero.subtitle": "Computer analyze 3 years of 4D & Toto data. Mixed with math patterns and a bit of 'Heng Ong Huat'!",
        "hero.disclaimer": "⚠️ FOR FUN ONLY — Don't bet your house/CPF!",

        // Status
        "status.loading": "Wait ah, loading...",
        "status.error": "Alamak, error loading data",
        "status.success": "Sweaty! Loaded {toto} Toto + {fourd} 4D draws",
        "status.notLoaded": "No data lei. Click 'Load Data' to start.",
        "status.action": "Load Data",

        // Stats
        "stats.4dDraws": "4D Draws",
        "stats.totoDraws": "Toto Draws",
        "stats.hotToto": "Hottest Toto #",
        "stats.overdue": "Si Beh Overdue",
        
        // Game Tabs
        "game.toto": "TOTO",
        "game.4d": "4D",

        // Dashboard
        "card.generator": "Number Generator",
        "strategy.weighted": "Weighted",
        "strategy.hot": "Hot Numbers",
        "strategy.cold": "Cold Numbers",
        "strategy.overdue": "Overdue",
        "strategy.balanced": "Balanced",
        "strategy.random": "Anyhow Hantam",
        "strategy.ai": "🤖 Smart Computer (AI)",
        
        "btn.generate": "🎯 Huat Ah!",
        "generator.explanation": "Select a pattern and generate your winning numbers",
        
        "details.title": "📖 How It Works (Simpler Term)",
        "details.weighted": "Mix of everything. Hot numbers + overdue numbers. The 'standard' logical choice.",
        "details.hot": "Numbers that always appear. The 'popular kids'.",
        "details.cold": "Numbers that rarely appear. Betting they will suddeny wake up.",
        "details.overdue": "Numbers that vanished for very long. 'Missing in action'.",
        "details.balanced": "Rojak mix: 2 hot + 2 overdue + 2 random. Covers all bases.",
        "details.random": "Anyhow pick one. Pure luck. Same chance as buying QuickPick.",
        "details.ai": "Like a super calculator. It studies the last 50 draws very hard to find secret patterns you cannot see. Good for those who want technology to help them think.",

        // Analysis
        "card.heatmap": "Frequency Heatmap",
        "heatmap.cold": "❄️ Cold",
        "heatmap.normal": "⚪ Normal",
        "heatmap.hot": "🔥 Hot",
        "card.overdue": "Long Time No See (Overdue)",
        "overdue.empty": "Click 'Load Data' first...",
        "card.distribution": "Number Frequency",

        // History
        "card.history": "Past Results",
        "table.draw": "Draw #",
        "table.date": "Date",
        "table.winning": "Winning Numbers",
        "table.additional": "Add.",
        "table.empty": "Empty like my wallet. Run scrapers first.",
        "pagination.page": "Page",

        // Footer
        "footer.disclaimer": "Mainly for fun/shiok only. Gambling implies risk. Please play responsibly.",

        // Donation Modal
        "modal.title": "🍍 Huat Ah! You Won?",
        "modal.subtitle": "Don't forget to share the Ong! 🧧",
        "modal.text": "Server electricity very expensive! If this bot helped you 'tiok' (strike) 4D or Toto, belanja (treat) me a Kopi or Beer to keep it alive!",
        "paynow.label": "PayNow to Mobile",
        "paynow.copy": "Tap number to copy",
        "paynow.alert": "Copied! Swee!"
    },
    zh: {
        // Nav
        "nav.dashboard": "主页",
        "nav.analysis": "数据分析",
        "nav.history": "历史记录",
        "nav.settings": "设置",
        "nav.donate": "捐赠",

        // Hero
        "hero.title": "预测您的 <span class='hero__title-gradient'>发财号码</span>",
        "hero.subtitle": "电脑分析3年的万字票和多多数据。结合数理逻辑和一点点'Heng Ong Huat'！",
        "hero.disclaimer": "⚠️ 仅供娱乐 — 小赌怡情，大赌伤身",

        // Status
        "status.loading": "正在加载... 等一下...",
        "status.error": "哎哟，加载出错了",
        "status.success": "搞定！加载了 {toto} 期多多 + {fourd} 期万字票",
        "status.notLoaded": "没数据咧。点一下 '加载数据'。",
        "status.action": "加载数据",

        // Stats
        "stats.4dDraws": "万字票期数",
        "stats.totoDraws": "多多期数",
        "stats.hotToto": "最旺多多号码",
        "stats.overdue": "最久没来",
        
        // Game Tabs
        "game.toto": "多多 (Toto)",
        "game.4d": "万字票 (4D)",

        // Dashboard
        "card.generator": "发财号码生成器",
        "strategy.weighted": "综合分析",
        "strategy.hot": "热门号码",
        "strategy.cold": "冷门号码",
        "strategy.overdue": "遗漏号码",
        "strategy.balanced": "罗惹 (Rojak) 组合",
        "strategy.random": "随便乱选",
        "strategy.ai": "🤖 智能电脑 (AI)",
        
        "btn.generate": "🎯 发啊 (Huat)",
        "generator.explanation": "选一个策略，看看你的运势",
        
        "details.title": "📖 简单说明",
        "details.weighted": "什么都有一点。热门+遗漏，最‘标准’的选法。",
        "details.hot": "经常开的号码。就是那些‘红人’。",
        "details.cold": "平时不出现的号码。赌它们突然‘醒’过来。",
        "details.overdue": "失踪最久的号码。",
        "details.balanced": "Rojak 混合：2个热门 + 2个遗漏 + 2个随机。大包围。",
        "details.random": "乱乱选。纯碰运气，跟买 QuickPick 一样。",
        "details.ai": "像个超级计算器。它帮你死命研究过去50期，找出你看不见的规律。不想动脑就用这个！",

        // Analysis
        "card.heatmap": "频率热力图",
        "heatmap.cold": "❄️ 冷",
        "heatmap.normal": "⚪ 一般",
        "heatmap.hot": "🔥 旺",
        "card.overdue": "失踪号码列表",
        "overdue.empty": "先加载数据...",
        "card.distribution": "号码频率",

        // History
        "card.history": "近期开奖",
        "table.draw": "期号",
        "table.date": "日期",
        "table.winning": "中奖号码",
        "table.additional": "特别号",
        "table.empty": "空空的。先运行爬虫。",
        "pagination.page": "页",

        // Footer
        "footer.disclaimer": "本工具纯属娱乐。主要为了爽。请理性投注。",

        // Donation Modal
        "modal.title": "🍍 发啊! 中奖了吗?",
        "modal.subtitle": "好运要分享! 🧧",
        "modal.text": "服务器也是要吃电的！如果帮你中了奖，请我喝杯 Kopi 或啤酒，让网站继续跑！",
        "paynow.label": "PayNow 手机号",
        "paynow.copy": "点击号码复制",
        "paynow.alert": "复制了！Swee！"
    },
    ms: {
        // Nav
        "nav.dashboard": "Utama",
        "nav.analysis": "Analisis",
        "nav.history": "Sejarah",
        "nav.settings": "Tetapan",
        "nav.donate": "Belanja Kopi",

        // Hero
        "hero.title": "Ramal Nombor <span class='hero__title-gradient'>Bertuah Anda</span>",
        "hero.subtitle": "Komputer analisis 3 tahun data. Campur matematik dan sikit nasib 'Huat'!",
        "hero.disclaimer": "⚠️ HANYA UNTUK SUKA-SUKA — Jangan gadai tanah!",

        // Status
        "status.loading": "Tunggu kejap...",
        "status.error": "Alamak, error pulak",
        "status.success": "Cun! {toto} Toto + {fourd} 4D dimuatkan",
        "status.notLoaded": "Tak ada data. Tekan 'Muat Data' dulu.",
        "status.action": "Muat Data",

        // Stats
        "stats.4dDraws": "Cabutan 4D",
        "stats.totoDraws": "Cabutan Toto",
        "stats.hotToto": "No. Paling Panas",
        "stats.overdue": "Paling Lama Hilang",
        
        // Game Tabs
        "game.toto": "TOTO",
        "game.4d": "4D",

        // Dashboard
        "card.generator": "Mesin Nombor",
        "strategy.weighted": "Campur-campur",
        "strategy.hot": "Nombor Panas",
        "strategy.cold": "Nombor Sejuk",
        "strategy.overdue": "Lama Hilang",
        "strategy.balanced": "Rojak",
        "strategy.random": "Hantam Saja",
        "strategy.ai": "🤖 Komputer Pintar (AI)",
        
        "btn.generate": "🎯 Huat Ah!",
        "generator.explanation": "Pilih strategi, tengok ong anda",
        
        "details.title": "📖 Penjelasan Mudah",
        "details.weighted": "Campuran frekuensi. Cuba nasib guna logik.",
        "details.hot": "Nombor yang selalu keluar.",
        "details.cold": "Nombor yang jarang keluar.",
        "details.overdue": "Nombor yang dah lama tak nampak.",
        "details.balanced": "Rojak: sikit panas, sikit sejuk, sikit random.",
        "details.random": "Main tikam saja. Macam QuickPick.",
        "details.ai": "Komputer ni tolong kaji 50 result lepas. Dia cari pattern yang mata kita tak nampak. Biar mesin buat kerja!",

        // Analysis
        "card.heatmap": "Peta Haba",
        "heatmap.cold": "❄️ Sejuk",
        "heatmap.normal": "⚪ Biasa",
        "heatmap.hot": "🔥 Panas",
        "card.overdue": "Nombor Lama Hilang",
        "overdue.empty": "Muat data dulu...",
        "card.distribution": "Taburan Nombor",

        // History
        "card.history": "Keputusan Lepas",
        "table.draw": "Cabutan #",
        "table.date": "Tarikh",
        "table.winning": "Nombor Kena",
        "table.additional": "Extra",
        "table.empty": "Kosong la. Jalankan scraper.",
        "pagination.page": "Muka",

        // Footer
        "footer.disclaimer": "Untuk hiburan saja. Jangan main gila-gila.",

        // Donation Modal
        "modal.title": "🍍 Huat Ah! Ada Kena?",
        "modal.subtitle": "Share sikit ong tu! 🧧",
        "modal.text": "Nak run server ni kena bayar bil letrik! Kalau apps ni tolong awak kena nombor, belanja la saya Kopi O satu!",
        "paynow.label": "PayNow ke Mobile",
        "paynow.copy": "Tekan nombor untuk copy",
        "paynow.alert": "Dah copy! Cantik!"
    },
    ta: {
        // Nav
        "nav.dashboard": "முகப்பு (Home)",
        "nav.analysis": "பகுப்பாய்வு",
        "nav.history": "வரலாறு",
        "nav.settings": "அமைப்புகள்",
        "nav.donate": "நன்கொடை",

        // Hero
        "hero.title": "உங்கள் <span class='hero__title-gradient'>அதிர்ஷ்ட எண்களை</span> கணிக்கவும்",
        "hero.subtitle": "3 வருட தரவு + சிறு அதிர்ஷ்டம்!",
        "hero.disclaimer": "⚠️ பொழுதுபோக்கிற்காக மட்டும்",

        // Status
        "status.loading": "காத்திருங்கள்...",
        "status.error": "பிழை ஏற்பட்டது",
        "status.success": "{toto} Toto + {fourd} 4D ஏற்றப்பட்டது",
        "status.notLoaded": "தரவு இல்லை. 'Load Data' அழுத்தவும்.",
        "status.action": "தரவை ஏற்றவும்",

        // Stats
        "stats.4dDraws": "4D குலுக்கல்கள்",
        "stats.totoDraws": "Toto குலுக்கல்கள்",
        "stats.hotToto": "அதிகம் வந்தவை",
        "stats.overdue": "நீண்ட நாள் வராதவை",
        
        // Game Tabs
        "game.toto": "TOTO",
        "game.4d": "4D",

        // Dashboard
        "card.generator": "எண் கணிப்பான்",
        "strategy.weighted": "கலவை முறை",
        "strategy.hot": "அதிகம் வந்தவை",
        "strategy.cold": "குறைவாக வந்தவை",
        "strategy.overdue": "தாமதமானவை",
        "strategy.balanced": "சமச்சீர் (Rojak)",
        "strategy.random": "சீரற்ற (Random)",
        "strategy.ai": "🤖 அறிவார்ந்த கணினி (AI)",
        
        "btn.generate": "🎯 எண்களை எடு!",
        "generator.explanation": "ஒரு முறையைத் தேர்வு செய்யவும்",
        
        "details.title": "📖 எளிய விளக்கம்",
        "details.weighted": "எல்லாம் கலந்த கலவை.",
        "details.hot": "அடிக்கடி வரும் எண்கள்.",
        "details.cold": "அரிதாக வரும் எண்கள்.",
        "details.overdue": "வெகு நாட்களாக வராத எண்கள்.",
        "details.balanced": "Rojak: 2 சூடான + 2 தாமதமான + 2 சீரற்ற.",
        "details.random": "அதிர்ஷ்டம் மட்டும். QuickPick போல.",
        "details.ai": "கடந்த 50 முடிவுகளை கணினி ஆராய்கிறது. நம் கண்ணுக்குத் தெரியாத வடிவங்களைக் கண்டுபிடிக்கும். கணினியை நம்புங்கள்!",

        // Analysis
        "card.heatmap": "வெப்ப வரைபடம்",
        "heatmap.cold": "❄️ குளிர்",
        "heatmap.normal": "⚪ இயல்பான",
        "heatmap.hot": "🔥 வெப்பம்",
        "card.overdue": "தாமதமான எண்கள்",
        "overdue.empty": "தரவை ஏற்றவும்...",
        "card.distribution": "எண் பரவல்",

        // History
        "card.history": "சமீபத்திய முடிவுகள்",
        "table.draw": "குலுக்கல் #",
        "table.date": "தேதி",
        "table.winning": "வெற்றி எண்கள்",
        "table.additional": "கூடுதல்",
        "table.empty": "தரவு இல்லை.",
        "pagination.page": "பக்கம்",

        // Footer
        "footer.disclaimer": "பொழுதுபோக்கிற்காக மட்டுமே. பொறுப்புடன் விளையாடவும்.",

        // Donation Modal
        "modal.title": "🍍 வெற்றி பெற்றீர்களா?",
        "modal.subtitle": "அதிர்ஷ்டத்தைப் பகிர்ந்து கொள்ளுங்கள்! 🧧",
        "modal.text": "சர்வர் கரண்ட் பில் கட்ட வேண்டும்! நீங்கள் வெற்றி பெற்றால், எனக்கு ஒரு காபி வாங்கித் தாருங்கள்!",
        "paynow.label": "PayNow Mobile",
        "paynow.copy": "நகலெடுக்க கிளிக் செய்யவும்",
        "paynow.alert": "நகலெடுக்கப்பட்டது! Super!"
    }
};
