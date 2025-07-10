// Teste simples para verificar se as traduções estão funcionando
import { useTranslation } from 'react-i18next';

export const TestTranslations = () => {
  const { t } = useTranslation();
  
  console.log('Testing team spending translations:');
  console.log('Title:', t('teamSpending.title'));
  console.log('Description:', t('teamSpending.description'));
  
  return null;
};
