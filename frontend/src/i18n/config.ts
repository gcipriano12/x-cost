
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import { DateTime } from 'luxon';

import en from './locales/en.json';
import pt from './locales/pt.json';

// Initialize i18next
i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: {
        translation: en
      },
      pt: {
        translation: pt
      }
    },
    fallbackLng: 'en',
    debug: false,
    interpolation: {
      escapeValue: false
    },
    detection: {
      // Configure language detection to use localStorage
      order: ['localStorage', 'navigator'],
      lookupLocalStorage: 'i18nextLng',
      caches: ['localStorage']
    }
  });

// Update locales with defaults if they're empty
if (Object.keys(en).length === 0) {
  i18n.addResourceBundle('en', 'translation', {
    common: {
      megabill: 'MegaBill',
      virtualTags: 'Virtual Tags',
      dashboard: 'Dashboard',
      costGuard: 'Cost Guard',
      anomalies: 'Anomalies',
      period: 'Period'
    },
    categories: {
      inform: 'Inform',
      optimize: 'Optimize',
      operate: 'Operate'
    },
    timeFilter: {
      last7days: 'Last 7 days',
      last30days: 'Last 30 days',
      last90days: 'Last 90 days',
      lastYear: 'Last year',
      custom: 'Custom range',
      selectPeriod: 'Select period'
    }
  }, true, true);
}

if (Object.keys(pt).length === 0) {
  i18n.addResourceBundle('pt', 'translation', {
    common: {
      megabill: 'MegaBill',
      virtualTags: 'Tags Virtuais',
      dashboard: 'Painel de Controle',
      costGuard: 'Guardião de Custos',
      anomalies: 'Anomalias',
      period: 'Período'
    },
    categories: {
      inform: 'Informar',
      optimize: 'Otimizar',
      operate: 'Operar'
    },
    timeFilter: {
      last7days: 'Últimos 7 dias',
      last30days: 'Últimos 30 dias',
      last90days: 'Últimos 90 dias',
      lastYear: 'Último ano',
      custom: 'Período personalizado',
      selectPeriod: 'Selecione o período'
    }
  }, true, true);
}

export default i18n;
