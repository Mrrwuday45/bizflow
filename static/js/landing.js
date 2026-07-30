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
        const targetStr = num.dataset.count;
        if (!targetStr) return;
        const target = parseFloat(targetStr.replace(/[^0-9.]/g, ''));
        const prefix = targetStr.match(/^[^0-9.]+/)?.[0] || '';
        const suffix = targetStr.match(/[^0-9.]+$|\+/)?.[0] || '';
        
        let start = 0;
        const duration = 1500;
        const stepTime = 30;
        const steps = duration / stepTime;
        const increment = target / steps;

        const timer = setInterval(() => {
          start += increment;
          if (start >= target) {
            num.innerText = targetStr;
            clearInterval(timer);
          } else {
            const formatted = Number.isInteger(target) ? Math.floor(start) : start.toFixed(1);
            num.innerText = `${prefix}${formatted}${suffix}`;
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
