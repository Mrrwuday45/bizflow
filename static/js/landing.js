/* BizFlow Landing Page Interactive Script */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lucide icons if available
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }

  // Navbar Scroll Effect
  const navbar = document.querySelector('.lp-navbar');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });

  // Interactive Live Demo Tabs
  const demoTabs = document.querySelectorAll('.lp-demo-tab');
  const demoPanes = document.querySelectorAll('.lp-demo-pane');

  demoTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetTab = tab.dataset.tab;

      demoTabs.forEach(t => t.classList.remove('active'));
      demoPanes.forEach(p => p.classList.remove('active'));

      tab.classList.add('active');
      const activePane = document.getElementById(`demo-${targetTab}`);
      if (activePane) {
        activePane.classList.add('active');
      }
    });
  });

  // Pricing Toggle (Monthly vs Annual)
  const billingToggle = document.getElementById('billing-toggle');
  const starterPrice = document.getElementById('price-starter');
  const proPrice = document.getElementById('price-pro');
  const enterprisePrice = document.getElementById('price-enterprise');

  if (billingToggle) {
    billingToggle.addEventListener('change', (e) => {
      const isAnnual = e.target.checked;

      if (isAnnual) {
        if (starterPrice) starterPrice.innerHTML = '$0 <span>/ year</span>';
        if (proPrice) proPrice.innerHTML = '$29 <span>/ month</span> <span style="font-size:0.75rem; color:#F472B6; display:block;">Billed annually ($348/yr)</span>';
        if (enterprisePrice) enterprisePrice.innerHTML = '$79 <span>/ month</span> <span style="font-size:0.75rem; color:#F472B6; display:block;">Billed annually ($948/yr)</span>';
      } else {
        if (starterPrice) starterPrice.innerHTML = '$0 <span>/ mo</span>';
        if (proPrice) proPrice.innerHTML = '$39 <span>/ mo</span>';
        if (enterprisePrice) enterprisePrice.innerHTML = '$99 <span>/ mo</span>';
      }
    });
  }

  // FAQ Accordion
  const faqItems = document.querySelectorAll('.lp-faq-item');
  faqItems.forEach(item => {
    const question = item.querySelector('.lp-faq-question');
    question.addEventListener('click', () => {
      const isActive = item.classList.contains('active');

      // Close all other items
      faqItems.forEach(i => i.classList.remove('active'));

      if (!isActive) {
        item.classList.add('active');
      }
    });
  });

  // Dynamic Real-Time Stats Fetching from Flask Backend API (/landing-stats)
  const fetchLandingStats = () => {
    fetch('/landing-stats')
      .then(res => res.json())
      .then(data => {
        if (!data) return;
        const elRev = document.getElementById('stat-revenue');
        const elInv = document.getElementById('stat-invoices');
        const elCust = document.getElementById('stat-customers');
        const elProd = document.getElementById('stat-products');

        if (elRev) {
          const revVal = data.monthly_revenue !== undefined ? data.monthly_revenue : (data.total_revenue || 0);
          elRev.dataset.count = revVal;
          elRev.innerText = `₹${revVal.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        }
        const elMonth = document.getElementById('stat-month-label');
        if (elMonth && data.current_month) {
          elMonth.innerText = data.current_month;
        }
        if (elInv) {
          elInv.dataset.count = data.invoice_count || 0;
          elInv.innerText = (data.invoice_count || 0).toLocaleString();
        }
        if (elCust) {
          elCust.dataset.count = data.customer_count || 0;
          elCust.innerText = (data.customer_count || 0).toLocaleString();
        }
        if (elProd) {
          elProd.dataset.count = data.product_count || 0;
          elProd.innerText = (data.product_count || 0).toLocaleString();
        }

        // Update mockup indicators
        document.querySelectorAll('.mockup-total-revenue').forEach(el => {
          el.innerText = `₹${(data.total_revenue || 0).toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        });
        document.querySelectorAll('.mockup-total-invoices').forEach(el => {
          el.innerText = (data.invoice_count || 0).toLocaleString();
        });
        document.querySelectorAll('.mockup-total-customers').forEach(el => {
          el.innerText = (data.customer_count || 0).toLocaleString();
        });
      })
      .catch(err => console.log('Notice: Stats API fetch:', err));
  };

  fetchLandingStats();

  // Animated Counter on Scroll for Metrics
  const metricNums = document.querySelectorAll('.lp-metric-num');
  let animated = false;

  const animateCounters = () => {
    if (animated) return;
    const metricsSection = document.querySelector('.lp-metrics-section');
    if (!metricsSection) return;

    const sectionPos = metricsSection.getBoundingClientRect().top;
    const screenPos = window.innerHeight / 1.2;

    if (sectionPos < screenPos) {
      animated = true;
      metricNums.forEach(num => {
        const targetStr = num.dataset.count || num.innerText;
        if (!targetStr) return;
        const target = parseFloat(targetStr.replace(/[^0-9.]/g, '')) || 0;
        const isCurrency = num.id === 'stat-revenue' || num.innerText.includes('₹');
        
        let start = 0;
        const duration = 1200;
        const stepTime = 30;
        const steps = duration / stepTime;
        const increment = target / steps;

        if (target === 0) {
          num.innerText = isCurrency ? '₹0.00' : '0';
          return;
        }

        const timer = setInterval(() => {
          start += increment;
          if (start >= target) {
            if (isCurrency) {
              num.innerText = `₹${target.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            } else {
              num.innerText = Math.round(target).toLocaleString();
            }
            clearInterval(timer);
          } else {
            if (isCurrency) {
              num.innerText = `₹${start.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            } else {
              num.innerText = Math.floor(start).toLocaleString();
            }
          }
        }, stepTime);
      });
    }
  };

  window.addEventListener('scroll', animateCounters);
  animateCounters(); // Trigger on load if already in view

  // Interactive Growth Savings Calculator
  const salesSlider = document.getElementById('calc-sales-slider');
  const sliderValDisplay = document.getElementById('calc-slider-val');
  const resHours = document.getElementById('calc-res-hours');
  const resRevenue = document.getElementById('calc-res-revenue');
  const resInvoices = document.getElementById('calc-res-invoices');
  const resInsights = document.getElementById('calc-res-insights');

  if (salesSlider) {
    salesSlider.addEventListener('input', (e) => {
      const sales = parseInt(e.target.value);
      if (sliderValDisplay) sliderValDisplay.innerText = `$${sales.toLocaleString()} / mo`;
      
      const hoursSaved = Math.round((sales / 1000) * 4.5 + 8);
      const estRevenueBoost = Math.round(sales * 0.22);
      const autoInvoices = Math.round(sales / 120);
      const aiInsights = Math.round(sales / 350 + 12);

      if (resHours) resHours.innerText = `${hoursSaved} Hrs`;
      if (resRevenue) resRevenue.innerText = `+$${estRevenueBoost.toLocaleString()}`;
      if (resInvoices) resInvoices.innerText = `${autoInvoices}`;
      if (resInsights) resInsights.innerText = `${aiInsights}`;
    });
  }
});
