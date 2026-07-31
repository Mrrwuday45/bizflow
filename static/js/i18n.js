/**
 * BizFlow AI Multilingual JavaScript Engine (i18n)
 * Handles client-side instant DOM translation, localStorage sync, and session updates.
 */

(function () {
    'use strict';

    // Supported Languages Metadata
    const LANGUAGES = {
        'en': 'English',
        'hi': 'हिन्दी',
        'te': 'తెలుగు',
        'ta': 'தமிழ்',
        'kn': 'ಕನ್ನಡ',
        'pa': 'ਪੰਜਾਬੀ',
        'mr': 'मराठी',
        'bn': 'বাংলা'
    };

    /**
     * Get active language code
     * Priority: localStorage -> HTML lang attribute -> 'en'
     */
    function getActiveLanguage() {
        const savedLang = localStorage.getItem('bizflow_lang');
        if (savedLang && LANGUAGES[savedLang]) {
            return savedLang;
        }
        const htmlLang = document.documentElement.lang;
        if (htmlLang && LANGUAGES[htmlLang]) {
            return htmlLang;
        }
        return 'en';
    }

    /**
     * Set language on server and update DOM
     */
    window.setBizFlowLanguage = function (langCode) {
        if (!LANGUAGES[langCode]) {
            langCode = 'en';
        }

        // Save to LocalStorage
        localStorage.setItem('bizflow_lang', langCode);
        document.documentElement.lang = langCode;

        // Sync with Flask Session via API
        fetch('/set-lang/' + langCode, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        }).catch(err => console.log('Lang sync notice:', err));

        // Translate current page DOM if translations dictionary is available
        applyDomTranslations(langCode);

        // Synchronize all dropdown selectors on the page
        const selectors = document.querySelectorAll('.bizflow-lang-select');
        selectors.forEach(select => {
            select.value = langCode;
        });
    };

    /**
     * Apply translations to elements with data-i18n and data-i18n-ph
     */
    function applyDomTranslations(langCode) {
        if (!window.BIZFLOW_TRANSLATIONS) return;
        const langDict = window.BIZFLOW_TRANSLATIONS[langCode] || window.BIZFLOW_TRANSLATIONS['en'];
        if (!langDict) return;

        // Text elements
        const textElements = document.querySelectorAll('[data-i18n]');
        textElements.forEach(el => {
            const key = el.getAttribute('data-i18n');
            const translation = langDict[key] || (window.BIZFLOW_TRANSLATIONS['en'] ? window.BIZFLOW_TRANSLATIONS['en'][key] : null);
            if (translation) {
                // If element has inner icons, preserve them if possible
                const icon = el.querySelector('i[data-lucide], svg');
                if (icon) {
                    const iconClone = icon.cloneNode(true);
                    el.textContent = ' ' + translation + ' ';
                    el.prepend(iconClone);
                } else {
                    el.textContent = translation;
                }
            }
        });

        // Placeholders
        const phElements = document.querySelectorAll('[data-i18n-ph]');
        phElements.forEach(el => {
            const key = el.getAttribute('data-i18n-ph');
            const translation = langDict[key] || (window.BIZFLOW_TRANSLATIONS['en'] ? window.BIZFLOW_TRANSLATIONS['en'][key] : null);
            if (translation) {
                el.placeholder = translation;
            }
        });

        // Titles / Tooltips
        const titleElements = document.querySelectorAll('[data-i18n-title]');
        titleElements.forEach(el => {
            const key = el.getAttribute('data-i18n-title');
            const translation = langDict[key] || (window.BIZFLOW_TRANSLATIONS['en'] ? window.BIZFLOW_TRANSLATIONS['en'][key] : null);
            if (translation) {
                el.title = translation;
            }
        });

        // Re-initialize Lucide icons if present
        if (window.lucide && typeof window.lucide.createIcons === 'function') {
            window.lucide.createIcons();
        }
    }

    // Initialize on DOM load
    document.addEventListener('DOMContentLoaded', function () {
        const activeLang = getActiveLanguage();
        
        // Fetch full translations dictionary if not pre-injected
        if (!window.BIZFLOW_TRANSLATIONS) {
            fetch('/api/translations')
                .then(res => res.json())
                .then(data => {
                    window.BIZFLOW_TRANSLATIONS = data;
                    window.setBizFlowLanguage(activeLang);
                })
                .catch(() => {
                    console.log('Using pre-injected or fallback translations.');
                    window.setBizFlowLanguage(activeLang);
                });
        } else {
            window.setBizFlowLanguage(activeLang);
        }

        // Attach listener to any language selector dropdowns
        document.body.addEventListener('change', function (e) {
            if (e.target && e.target.classList.contains('bizflow-lang-select')) {
                window.setBizFlowLanguage(e.target.value);
            }
        });
    });
})();
