import subprocess
import os

html_content = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Медиакит anvrsk.ru 2026 | Реклама и спецпроекты</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    @page {
      size: A4 portrait;
      margin: 0;
    }
    
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }

    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #f8fafc;
      color: #0f172a;
      line-height: 1.45;
    }

    .page {
      width: 210mm;
      height: 297mm;
      min-height: 297mm;
      max-height: 297mm;
      padding: 16mm 18mm;
      position: relative;
      background: #ffffff;
      page-break-after: always;
      page-break-inside: avoid;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }

    /* Page Header */
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 2px solid #e2e8f0;
      padding-bottom: 12px;
      margin-bottom: 18px;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .logo-badge {
      width: 40px;
      height: 40px;
      border-radius: 10px;
      background: linear-gradient(135deg, #0284c7, #1e40af);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-weight: 900;
      font-size: 20px;
      box-shadow: 0 4px 10px rgba(2, 132, 199, 0.3);
    }

    .brand-text h1 {
      font-size: 18px;
      font-weight: 800;
      color: #0f172a;
      letter-spacing: -0.5px;
    }

    .brand-text span {
      color: #0284c7;
    }

    .brand-text p {
      font-size: 10px;
      color: #64748b;
      font-weight: 500;
    }

    .badge-doc {
      background: #f1f5f9;
      border: 1px solid #cbd5e1;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 700;
      color: #334155;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    /* Page Footer */
    .footer {
      border-top: 1px solid #e2e8f0;
      padding-top: 10px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 10px;
      color: #64748b;
    }

    .footer a {
      color: #0284c7;
      text-decoration: none;
      font-weight: 600;
    }

    /* Content components */
    .hero-banner {
      background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #0369a1 100%);
      color: white;
      border-radius: 18px;
      padding: 24px 26px;
      margin-bottom: 20px;
      box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.3);
    }

    .hero-banner h2 {
      font-size: 24px;
      font-weight: 800;
      line-height: 1.25;
      margin-bottom: 10px;
      letter-spacing: -0.5px;
    }

    .hero-banner p {
      font-size: 12.5px;
      color: #cbd5e1;
      line-height: 1.5;
      max-width: 90%;
    }

    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin-bottom: 22px;
    }

    .metric-card {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 14px;
      padding: 14px 12px;
      text-align: center;
      transition: all 0.2s;
    }

    .metric-val {
      font-size: 22px;
      font-weight: 900;
      color: #0284c7;
      line-height: 1.1;
      margin-bottom: 4px;
    }

    .metric-lbl {
      font-size: 10px;
      font-weight: 700;
      color: #475569;
      text-transform: uppercase;
      letter-spacing: 0.3px;
    }

    .metric-desc {
      font-size: 9.5px;
      color: #64748b;
      margin-top: 3px;
    }

    .section-title {
      font-size: 15px;
      font-weight: 800;
      color: #0f172a;
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 12px;
    }

    .section-title::before {
      content: '';
      display: block;
      width: 4px;
      height: 16px;
      background: #0284c7;
      border-radius: 2px;
    }

    .audience-cards {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      margin-bottom: 20px;
    }

    .aud-card {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 14px;
      padding: 14px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }

    .aud-icon {
      font-size: 20px;
      margin-bottom: 6px;
    }

    .aud-title {
      font-size: 12px;
      font-weight: 800;
      color: #0f172a;
      margin-bottom: 4px;
    }

    .aud-desc {
      font-size: 10px;
      color: #64748b;
      line-height: 1.4;
    }

    .features-list {
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      border-radius: 14px;
      padding: 14px 18px;
    }

    .features-list h4 {
      font-size: 12px;
      font-weight: 800;
      color: #166534;
      margin-bottom: 6px;
    }

    .features-list ul {
      list-style: none;
      font-size: 10.5px;
      color: #15803d;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
    }

    .features-list li::before {
      content: '✓ ';
      font-weight: 900;
      color: #16a34a;
    }

    /* PAGE 2 STYLES */
    .format-card {
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 14px;
      padding: 14px 16px;
      margin-bottom: 14px;
      box-shadow: 0 3px 8px rgba(0,0,0,0.03);
    }

    .format-head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }

    .format-name {
      font-size: 14px;
      font-weight: 800;
      color: #0f172a;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .format-tag {
      font-size: 9px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      text-transform: uppercase;
    }

    .tag-blue { background: #e0f2fe; color: #0369a1; }
    .tag-amber { background: #fef3c7; color: #b45309; }
    .tag-emerald { background: #d1fae5; color: #047857; }

    .format-body {
      font-size: 11px;
      color: #475569;
      line-height: 1.45;
      margin-bottom: 10px;
    }

    .format-specs {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 8px 12px;
      font-size: 10px;
    }

    .spec-item span {
      display: block;
      color: #64748b;
      font-size: 9px;
    }

    .spec-item strong {
      color: #0f172a;
      font-size: 10.5px;
    }

    /* Mockups display */
    .mockups-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-top: 10px;
    }

    .mockup-box {
      border: 1px dashed #cbd5e1;
      border-radius: 12px;
      padding: 10px;
      background: #f1f5f9;
      text-align: center;
    }

    .mockup-inner {
      background: white;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 8px;
      font-size: 10px;
      color: #334155;
    }

    /* PAGE 3 STYLES: PRICING */
    .pricing-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 14px;
      margin-bottom: 18px;
    }

    .price-card {
      background: white;
      border: 1px solid #e2e8f0;
      border-radius: 16px;
      padding: 18px 16px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      position: relative;
      box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }

    .price-card.featured {
      border: 2px solid #f59e0b;
      background: #fffdfa;
      box-shadow: 0 10px 25px -5px rgba(245, 158, 11, 0.2);
    }

    .popular-badge {
      position: absolute;
      top: -10px;
      left: 50%;
      transform: translateX(-50%);
      background: #f59e0b;
      color: #0f172a;
      font-size: 8.5px;
      font-weight: 900;
      text-transform: uppercase;
      padding: 2px 10px;
      border-radius: 20px;
      letter-spacing: 0.5px;
    }

    .plan-title {
      font-size: 13px;
      font-weight: 800;
      color: #0f172a;
      text-transform: uppercase;
      margin-bottom: 6px;
    }

    .plan-price {
      font-size: 26px;
      font-weight: 900;
      color: #0f172a;
      line-height: 1;
      margin-bottom: 4px;
    }

    .plan-period {
      font-size: 10px;
      color: #64748b;
      margin-bottom: 12px;
      border-bottom: 1px solid #e2e8f0;
      padding-bottom: 8px;
    }

    .plan-features {
      list-style: none;
      font-size: 10.5px;
      color: #475569;
      space-y: 6px;
      margin-bottom: 14px;
    }

    .plan-features li {
      margin-bottom: 6px;
      display: flex;
      align-items: flex-start;
      gap: 6px;
    }

    .plan-features li span {
      color: #0284c7;
      font-weight: 900;
    }

    .plan-target {
      font-size: 9.5px;
      background: #f1f5f9;
      padding: 6px 8px;
      border-radius: 8px;
      color: #475569;
      font-style: italic;
    }

    /* Comparison Table */
    .comp-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 10px;
      margin-top: 10px;
      border-radius: 10px;
      overflow: hidden;
      border: 1px solid #e2e8f0;
    }

    .comp-table th {
      background: #f1f5f9;
      padding: 8px 10px;
      text-align: left;
      font-weight: 700;
      color: #334155;
      border-bottom: 1px solid #cbd5e1;
    }

    .comp-table td {
      padding: 7px 10px;
      border-bottom: 1px solid #f1f5f9;
      color: #475569;
    }

    .comp-table tr:last-child td {
      border-bottom: none;
    }

    /* PAGE 4 STYLES: LEGAL, SPECS & CONTACTS */
    .two-cols {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 20px;
    }

    .info-block {
      background: white;
      border: 1px solid #e2e8f0;
      border-radius: 14px;
      padding: 16px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }

    .info-block h3 {
      font-size: 13px;
      font-weight: 800;
      color: #0f172a;
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .info-block p, .info-block li {
      font-size: 10.5px;
      color: #475569;
      line-height: 1.45;
    }

    .info-block ul {
      margin-left: 14px;
      margin-top: 6px;
    }

    .steps-chain {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 10px;
      margin-bottom: 22px;
    }

    .step-item {
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      border-radius: 12px;
      padding: 12px 10px;
      text-align: center;
      position: relative;
    }

    .step-num {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: #0284c7;
      color: white;
      font-weight: 800;
      font-size: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 6px auto;
    }

    .step-name {
      font-size: 11px;
      font-weight: 700;
      color: #0f172a;
      margin-bottom: 3px;
    }

    .step-desc {
      font-size: 9px;
      color: #64748b;
    }

    .cta-card {
      background: linear-gradient(135deg, #0284c7 0%, #0369a1 50%, #075985 100%);
      color: white;
      border-radius: 18px;
      padding: 22px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 10px 25px -5px rgba(2, 132, 199, 0.4);
    }

    .cta-text h3 {
      font-size: 18px;
      font-weight: 800;
      margin-bottom: 4px;
    }

    .cta-text p {
      font-size: 11.5px;
      color: #e0f2fe;
      line-height: 1.4;
    }

    .contact-badge {
      background: white;
      color: #0369a1;
      border-radius: 12px;
      padding: 12px 18px;
      text-align: center;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      flex-shrink: 0;
    }

    .contact-badge a {
      color: #0284c7;
      font-weight: 800;
      font-size: 14px;
      text-decoration: none;
      display: block;
    }

    .contact-badge span {
      font-size: 10px;
      color: #64748b;
      display: block;
      margin-top: 2px;
    }
  </style>
</head>
<body>

  <!-- ==================== СТРАНИЦА 1 ==================== -->
  <div class="page">
    <div>
      <div class="header">
        <div class="brand">
          <div class="logo-badge">⚓</div>
          <div class="brand-text">
            <h1>Актуальный <span>Новороссийск</span></h1>
            <p>anvrsk.ru • Городской веб-дашборд и инфоканал</p>
          </div>
        </div>
        <div class="badge-doc">Медиакит & Прайс-лист 2026</div>
      </div>

      <div class="hero-banner">
        <h2>Реклама для бизнеса<br>в главном городском дашборде</h2>
        <p>
          <strong>anvrsk.ru</strong> — единая независимая точка доступа к оперативной информации Новороссийска: дорожные камеры Шесхариса и перевалов, сила норд-оста и боры, морские рейсы, подача воды ТГВ и сводки служб 112.
        </p>
      </div>

      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-val">45 000+</div>
          <div class="metric-lbl">Уникальных жителей</div>
          <div class="metric-desc">ежемесячная аудитория</div>
        </div>
        <div class="metric-card">
          <div class="metric-val">180 000+</div>
          <div class="metric-lbl">Просмотров страниц</div>
          <div class="metric-desc">высокая частота визитов</div>
        </div>
        <div class="metric-card">
          <div class="metric-val">3.2 мин</div>
          <div class="metric-lbl">Длительность сессии</div>
          <div class="metric-desc">внимательное изучение</div>
        </div>
        <div class="metric-card">
          <div class="metric-val">до 2.8%</div>
          <div class="metric-lbl">CTR баннеров</div>
          <div class="metric-desc">без слепой зоны</div>
        </div>
      </div>

      <div class="section-title">Целевая аудитория портала</div>
      <div class="audience-cards">
        <div class="aud-card">
          <div class="aud-icon">🚛</div>
          <div class="aud-title">Логистика, порт и водители</div>
          <div class="aud-desc">
            Экспедиторы, водители большегрузов на въезде в НМТП, логистические компании, диспетчеры. Следят за Шесхарисом, перевалом «Волчьи ворота» и силой ветра.
          </div>
        </div>
        <div class="aud-card">
          <div class="aud-icon">🏘️</div>
          <div class="aud-title">Платежеспособные новороссийцы</div>
          <div class="aud-desc">
            Владельцы квартир и домов, семьи с детьми, покупатели авто и недвижимости. Ежедневно проверяют графики подачи воды ТГВ, отключения света и погоду на завтра.
          </div>
        </div>
        <div class="aud-card">
          <div class="aud-icon">💼</div>
          <div class="aud-title">Бизнес и предприниматели</div>
          <div class="aud-desc">
            Руководители местных производств, подрядчики, владельцы складов, заведений и сервисов. Читают раздел «Новости бизнеса» и сводки Главы города.
          </div>
        </div>
      </div>

      <div class="features-list">
        <h4>Почему реклама на anvrsk.ru работает эффективнее соцсетей:</h4>
        <ul>
          <li><strong>Не больше 4 баннеров на весь сайт:</strong> никакой баннерной слепоты и конкурентной свалки.</li>
          <li><strong>100% Share of Voice:</strong> ваш баннер виден всегда, а не теряется в алгоритмической ленте.</li>
          <li><strong>Утилитарный трафик:</strong> люди заходят с конкретной задачей (проверить проезд, ветер, воду), уровень доверия максимальный.</li>
          <li><strong>Полная маркировка erid:</strong> официальное размещение с регистрацией в ЕРИР Роскомнадзора по закону РФ.</li>
        </ul>
      </div>
    </div>

    <div class="footer">
      <span>Актуальный Новороссийск • Медиакит для рекламодателей 2026</span>
      <span>Связь с коммерческим отделом: <a href="mailto:advobv@gmail.com">advobv@gmail.com</a></span>
      <span>Стр. 1 из 4</span>
    </div>
  </div>

  <!-- ==================== СТРАНИЦА 2 ==================== -->
  <div class="page">
    <div>
      <div class="header">
        <div class="brand">
          <div class="logo-badge">⚓</div>
          <div class="brand-text">
            <h1>Форматы размещения <span>и витрина</span></h1>
            <p>Премиальные слоты с максимальной конверсией</p>
          </div>
        </div>
        <div class="badge-doc">Форматы рекламы</div>
      </div>

      <!-- FORMAT 1 -->
      <div class="format-card">
        <div class="format-head">
          <div class="format-name">
            <span>📌 Формат 1: Сквозные боковые баннеры (Desktop & Mobile)</span>
          </div>
          <span class="format-tag tag-blue">Лимитировано: 4 места</span>
        </div>
        <div class="format-body">
          Премиальные карточки, зафиксированные по бокам основного контента дашборда (2 слота слева, 2 справа). Находятся в поле зрения пользователя при скролле сводок, дорожных камер и карты. На смартфонах элегантно трансформируются в верхний интерактивный слайдер над лентой.
        </div>
        <div class="format-specs">
          <div class="spec-item">
            <span>Размещение</span>
            <strong>Сквозное (все разделы)</strong>
          </div>
          <div class="spec-item">
            <span>Размер карточки</span>
            <strong>280 × 220 px (desktop)</strong>
          </div>
          <div class="spec-item">
            <span>Кликабельность</span>
            <strong>Кнопка прямого действия</strong>
          </div>
          <div class="spec-item">
            <span>Юридический erid</span>
            <strong>Интегрирован в угол</strong>
          </div>
        </div>
      </div>

      <!-- FORMAT 2 -->
      <div class="format-card">
        <div class="format-head">
          <div class="format-name">
            <span>📰 Формат 2: Раздел «Новости бизнеса» (Пресс-релизы и статьи)</span>
          </div>
          <span class="format-tag tag-amber">Нативный PR</span>
        </div>
        <div class="format-body">
          Полноразмерные публикация о вашей компании, продукте, старте продаж в ЖК или открытии филиала. Пресс-релиз размещается в выделенной вкладке «Новости бизнеса», анонсируется в общей ленте и закрепляется на главной странице. Отлично индексируется Яндексом.
        </div>
        <div class="format-specs">
          <div class="spec-item">
            <span>Объем текста</span>
            <strong>до 5 000 знаков</strong>
          </div>
          <div class="spec-item">
            <span>Иллюстрации</span>
            <strong>до 5 фото + логотип</strong>
          </div>
          <div class="spec-item">
            <span>Ссылки</span>
            <strong>Прямые с UTM-метками</strong>
          </div>
          <div class="spec-item">
            <span>Срок жизни</span>
            <strong>Навсегда в архиве</strong>
          </div>
        </div>
      </div>

      <!-- FORMAT 3 -->
      <div class="format-card">
        <div class="format-head">
          <div class="format-name">
            <span>🗺️ Формат 3: Брендированная метка на интерактивной карте города</span>
          </div>
          <span class="format-tag tag-emerald">Гео-маркетинг</span>
        </div>
        <div class="format-body">
          Установка кастомной фирменной метки вашего объекта (офис продаж, склад, терминал, автосалон, отель) на карте реального времени Новороссийска. При клике открывается брендированная карточка с описанием, фото и кнопкой маршрута/перехода.
        </div>
        <div class="format-specs">
          <div class="spec-item">
            <span>Локация</span>
            <strong>Точные GPS-координаты</strong>
          </div>
          <div class="spec-item">
            <span>Карточка</span>
            <strong>Фото, телефон, сайт</strong>
          </div>
          <div class="spec-item">
            <span>Подложка</span>
            <strong>Спутник Esri / Схема</strong>
          </div>
          <div class="spec-item">
            <span>Эксклюзивность</span>
            <strong>До 2 меток в микрорайоне</strong>
          </div>
        </div>
      </div>

      <div class="section-title">Примеры рекламодателей, для которых портал идеален:</div>
      <div class="mockups-grid">
        <div class="mockup-box">
          <div class="mockup-inner">
            <strong>B2B и Логистика:</strong> Складские комплексы, контейнерные терминалы, экспедирование, грузовой шиномонтаж и запчасти на въезде в город (Шесхарис/Цемдолина).
          </div>
        </div>
        <div class="mockup-box">
          <div class="mockup-inner">
            <strong>B2C и Недвижимость:</strong> Застройщики (старт продаж ЖК в Южном и Центральном р-нах), автосалоны, частные клиники, отели и туристические сервисы.
          </div>
        </div>
      </div>
    </div>

    <div class="footer">
      <span>Актуальный Новороссийск • anvrsk.ru</span>
      <span>Бронирование мест: <a href="mailto:advobv@gmail.com">advobv@gmail.com</a></span>
      <span>Стр. 2 из 4</span>
    </div>
  </div>

  <!-- ==================== СТРАНИЦА 3 ==================== -->
  <div class="page">
    <div>
      <div class="header">
        <div class="brand">
          <div class="logo-badge">⚓</div>
          <div class="brand-text">
            <h1>Прайс-лист <span>и пакеты</span></h1>
            <p>Прозрачное ценообразование без скрытых наценок</p>
          </div>
        </div>
        <div class="badge-doc">Тарифы 2026</div>
      </div>

      <div class="pricing-grid">
        <!-- PLAN 1 -->
        <div class="price-card">
          <div>
            <div class="plan-title" style="color: #0284c7;">Пресс-релиз</div>
            <div class="plan-price">4 500 ₽</div>
            <div class="plan-period">разовая публикация</div>
            <ul class="plan-features">
              <li><span>✓</span> Раздел «Новости бизнеса»</li>
              <li><span>✓</span> Закрепление на 48 часов</li>
              <li><span>✓</span> До 5 000 знаков и 5 фото</li>
              <li><span>✓</span> Прямые ссылки с UTM</li>
              <li><span>✓</span> Маркировка erid в ОРД</li>
              <li><span>✓</span> Навсегда в архиве сайта</li>
            </ul>
          </div>
          <div class="plan-target">Идеально для разовых новостей, акций, открытий и PR-поводов.</div>
        </div>

        <!-- PLAN 2 (FEATURED) -->
        <div class="price-card featured">
          <div class="popular-badge">Хит продаж</div>
          <div>
            <div class="plan-title" style="color: #d97706;">Боковой баннер</div>
            <div class="plan-price">12 000 ₽</div>
            <div class="plan-period">в месяц (сквозной)</div>
            <ul class="plan-features">
              <li><span>✓</span> <strong>Сквозной показ на всех страницах</strong></li>
              <li><span>✓</span> 1 из 4 эксклюзивных слотов</li>
              <li><span>✓</span> 100% показов (без ротации)</li>
              <li><span>✓</span> Кнопка перехода / CTA</li>
              <li><span>✓</span> Адаптив для смартфонов</li>
              <li><span>✓</span> Ежемесячный отчет Метрики</li>
              <li><span>✓</span> Маркировка erid включена</li>
            </ul>
          </div>
          <div class="plan-target">Максимальный охват и постоянное присутствие бренда на глазах у города.</div>
        </div>

        <!-- PLAN 3 -->
        <div class="price-card">
          <div>
            <div class="plan-title" style="color: #4f46e5;">Генеральный партнер</div>
            <div class="plan-price">25 000 ₽</div>
            <div class="plan-period">в месяц (эксклюзив)</div>
            <ul class="plan-features">
              <li><span>✓</span> Сквозной баннер №1 (верхняя позиция)</li>
              <li><span>✓</span> <strong>2 пресс-релиза в месяц включено</strong></li>
              <li><span>✓</span> Фирменная метка на карте города</li>
              <li><span>✓</span> Брендирование раздела «Камеры»</li>
              <li><span>✓</span> Персональный дизайнер макетов</li>
              <li><span>✓</span> Приоритетная поддержка 24/7</li>
            </ul>
          </div>
          <div class="plan-target">Комплексное доминирование на рынке Новороссийска для лидеров отраслей.</div>
        </div>
      </div>

      <div class="section-title">Сравнение опций в пакетах размещения</div>
      <table class="comp-table">
        <thead>
          <tr>
            <th>Возможность / Опция</th>
            <th>Пресс-релиз</th>
            <th>Боковой баннер</th>
            <th>Генеральный партнер</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Сквозной баннер на ПК и мобильных</strong></td>
            <td>—</td>
            <td>Да (100% показов)</td>
            <td>Да (приоритетный №1)</td>
          </tr>
          <tr>
            <td><strong>Публикация статей в «Новостях бизнеса»</strong></td>
            <td>1 публикация</td>
            <td>Скидка 50%</td>
            <td><strong>2 статьи в месяц</strong></td>
          </tr>
          <tr>
            <td><strong>Метка компании на интерактивной карте</strong></td>
            <td>—</td>
            <td>Опционально (+2 000 ₽)</td>
            <td><strong>Включена в пакет</strong></td>
          </tr>
          <tr>
            <td><strong>Официальная маркировка (erid) по закону</strong></td>
            <td>Включена</td>
            <td>Включена</td>
            <td>Включена под ключ</td>
          </tr>
          <tr>
            <td><strong>Статистика переходов и показов</strong></td>
            <td>По запросу</td>
            <td>Ежемесячный отчет</td>
            <td>Еженедельный отчет</td>
          </tr>
        </tbody>
      </table>

      <div style="margin-top: 14px; background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px; padding: 10px 14px; display: flex; justify-content: space-between; align-items: center; font-size: 10.5px; color: #1e40af;">
        <span>🔥 <strong>Скидки при длительном бронировании:</strong> при оплате за 3 месяца — <strong>скидка 15%</strong>, при оплате за 6 месяцев — <strong>скидка 25%</strong>.</span>
      </div>
    </div>

    <div class="footer">
      <span>Актуальный Новороссийск • anvrsk.ru</span>
      <span>Вопросы по тарифам: <a href="mailto:advobv@gmail.com">advobv@gmail.com</a></span>
      <span>Стр. 3 из 4</span>
    </div>
  </div>

  <!-- ==================== СТРАНИЦА 4 ==================== -->
  <div class="page">
    <div>
      <div class="header">
        <div class="brand">
          <div class="logo-badge">⚓</div>
          <div class="brand-text">
            <h1>Маркировка, техтребования <span>и контакты</span></h1>
            <p>100% соблюдение ФЗ-347 и быстрый запуск за 24 часа</p>
          </div>
        </div>
        <div class="badge-doc">Регламент & Заказ</div>
      </div>

      <div class="two-cols">
        <div class="info-block">
          <h3>📐 Технические требования</h3>
          <p><strong>Для боковых баннеров:</strong></p>
          <ul>
            <li>Форматы: WebP, PNG, JPG, векторный SVG</li>
            <li>Размер Desktop: 280 × 220 px (или 560 × 440 px для Retina)</li>
            <li>Размер Mobile: 600 × 220 px (горизонтальный)</li>
            <li>Вес файла: до 250 КБ</li>
            <li>Текст: четкий заголовок, оффер, логотип и кнопка CTA</li>
          </ul>
          <p style="margin-top: 8px;"><strong>Для пресс-релизов:</strong></p>
          <ul>
            <li>Текст в DOCX / TXT / Google Docs (до 5 000 знаков)</li>
            <li>До 5 фотографий (1920 × 1080 px)</li>
            <li>Ссылка на сайт компании с UTM-метками</li>
          </ul>
        </div>

        <div class="info-block">
          <h3>⚖️ Маркировка рекламы (№ 347-ФЗ)</h3>
          <p>
            Мы полностью берем на себя юридическую рутину по закону о рекламе:
          </p>
          <ul>
            <li>Регистрируем каждый креатив в официальном <strong>ОРД (Операторе рекламных данных)</strong> до старта показа.</li>
            <li>Присваиваем уникальный токен <strong>erid</strong> и наносим его на макет.</li>
            <li>Ежемесячно передаем отчеты о показах и разаллокации в <strong>ЕРИР Роскомнадзора</strong>.</li>
            <li>Предоставляем закрывающие акты и чеки для юрлиц и ИП.</li>
          </ul>
          <p style="margin-top: 6px; font-weight: 700; color: #15803d;">
            Для вас всё законно, прозрачно и без риска штрафов!
          </p>
        </div>
      </div>

      <div class="section-title">Как начать сотрудничество (4 простых шага):</div>
      <div class="steps-chain">
        <div class="step-item">
          <div class="step-num">1</div>
          <div class="step-name">Заявка</div>
          <div class="step-desc">Напишите нам на почту с указанием формата и компании</div>
        </div>
        <div class="step-item">
          <div class="step-num">2</div>
          <div class="step-name">Договор</div>
          <div class="step-desc">Согласуем даты бронирования, договор и счет (для ООО/ИП/СЗ)</div>
        </div>
        <div class="step-item">
          <div class="step-num">3</div>
          <div class="step-name">Регистрация</div>
          <div class="step-desc">Проверяем макет, регистрируем erid в ОРД за 1 час</div>
        </div>
        <div class="step-item">
          <div class="step-num">4</div>
          <div class="step-name">Старт показов</div>
          <div class="step-desc">Размещение на anvrsk.ru и предоставление статистики</div>
        </div>
      </div>

      <div class="cta-card">
        <div class="cta-text">
          <h3>Забронируйте рекламное место уже сегодня!</h3>
          <p>
            Количество партнерских баннеров ограничено 4 местами во избежание перегрузки аудитории. Проверьте доступность слотов на текущий месяц.
          </p>
        </div>
        <div class="contact-badge">
          <span style="font-size: 9px; text-transform: uppercase; font-weight: 700; color: #64748b;">Отдел рекламы</span>
          <a href="mailto:advobv@gmail.com?subject=anvrsk-ru">advobv@gmail.com</a>
          <span>Тема: <strong>anvrsk-ru</strong></span>
        </div>
      </div>
    </div>

    <div class="footer">
      <span>Актуальный Новороссийск (anvrsk.ru) • Краснодарский край, г. Новороссийск</span>
      <span>Сайт: <a href="https://anvrsk.ru">anvrsk.ru</a> • Email: <a href="mailto:advobv@gmail.com">advobv@gmail.com</a></span>
      <span>Стр. 4 из 4</span>
    </div>
  </div>

</body>
</html>
"""

with open('mediakit.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("[1/2] mediakit.html created successfully.")

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(edge_path):
    edge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

html_abs = os.path.abspath('mediakit.html')
pdf_abs = os.path.abspath('anvrsk_mediakit_2026.pdf')

cmd = [
    edge_path,
    "--headless=new",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_abs}",
    html_abs
]

res = subprocess.run(cmd, capture_output=True, text=True)
if os.path.exists(pdf_abs) and os.path.getsize(pdf_abs) > 5000:
    print(f"[2/2] anvrsk_mediakit_2026.pdf generated successfully! Size: {os.path.getsize(pdf_abs)} bytes.")
else:
    print(f"[ERR] Failed to generate PDF: {res.stderr}")
