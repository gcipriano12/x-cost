import React, { useState } from 'react';
import Dashboard from '@/components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { Settings as SettingsIcon, Globe, Bell, Shield, Palette, Monitor } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { useTheme } from '@/components/theme/ThemeProvider';
import { useTranslation } from 'react-i18next';

const Settings = () => {
  const { theme, setTheme } = useTheme();
  const { i18n, t } = useTranslation();
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    anomalies: true,
    budgetAlerts: true,
    weeklyReports: false
  });

  const handleLanguageChange = (language: string) => {
    i18n.changeLanguage(language);
  };

  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <PageHeader 
          icon={SettingsIcon} 
          title={t('common.appearance')} 
          color="text-gray-600"
        />
        
        <div className="p-4 space-y-6">
          {/* Appearance Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5" />
                {t('common.appearance')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-base">{t('common.theme')}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t('common.chooseTheme')}
                  </p>
                </div>
                <Select value={theme} onValueChange={setTheme}>
                  <SelectTrigger className="w-40">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="light">{t('common.light')}</SelectItem>
                    <SelectItem value="dark">{t('common.dark')}</SelectItem>
                    <SelectItem value="system">{t('common.system')}</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Language Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                {t('common.languageRegion')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-base">{t('common.language')}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t('common.selectLanguage')}
                  </p>
                </div>
                <Select value={i18n.language} onValueChange={handleLanguageChange}>
                  <SelectTrigger className="w-40">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="pt">Português</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-base">{t('common.currency')}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t('common.defaultCurrency')}
                  </p>
                </div>
                <Select defaultValue="usd">
                  <SelectTrigger className="w-40">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="usd">USD ($)</SelectItem>
                    <SelectItem value="brl">BRL (R$)</SelectItem>
                    <SelectItem value="eur">EUR (€)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Notification Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                {t('common.notifications')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-base">{t('common.emailNotifications')}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t('common.receiveEmailNotifications')}
                  </p>
                </div>
                <Switch
                  checked={notifications.email}
                  onCheckedChange={(checked) => 
                    setNotifications(prev => ({ ...prev, email: checked }))
                  }
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-base">{t('common.pushNotifications')}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t('common.receivePushNotifications')}
                  </p>
                </div>
                <Switch
                  checked={notifications.push}
                  onCheckedChange={(checked) => 
                    setNotifications(prev => ({ ...prev, push: checked }))
                  }
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-base">{t('common.anomalyAlerts')}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t('common.getAnomalyNotifications')}
                  </p>
                </div>
                <Switch
                  checked={notifications.anomalies}
                  onCheckedChange={(checked) => 
                    setNotifications(prev => ({ ...prev, anomalies: checked }))
                  }
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-base">{t('common.budgetAlerts')}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t('common.budgetLimitAlerts')}
                  </p>
                </div>
                <Switch
                  checked={notifications.budgetAlerts}
                  onCheckedChange={(checked) => 
                    setNotifications(prev => ({ ...prev, budgetAlerts: checked }))
                  }
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-base">{t('common.weeklyReports')}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t('common.weeklyReportsSummary')}
                  </p>
                </div>
                <Switch
                  checked={notifications.weeklyReports}
                  onCheckedChange={(checked) => 
                    setNotifications(prev => ({ ...prev, weeklyReports: checked }))
                  }
                />
              </div>
            </CardContent>
          </Card>

          {/* Data & Privacy Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                {t('common.dataPrivacy')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-base">{t('common.dataRetention')}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t('common.dataRetentionDescription')}
                  </p>
                </div>
                <Select defaultValue="12months">
                  <SelectTrigger className="w-40">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="6months">6 months</SelectItem>
                    <SelectItem value="12months">12 months</SelectItem>
                    <SelectItem value="24months">24 months</SelectItem>
                    <SelectItem value="indefinite">Indefinite</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-base">{t('common.analyticsTracking')}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t('common.analyticsTrackingDescription')}
                  </p>
                </div>
                <Switch defaultChecked />
              </div>
            </CardContent>
          </Card>

          {/* Advanced Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Monitor className="h-5 w-5" />
                {t('common.advanced')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-base">{t('common.autoRefreshDashboard')}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t('common.autoRefreshDescription')}
                  </p>
                </div>
                <Switch defaultChecked />
              </div>
              
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-base">{t('common.debugMode')}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t('common.debugModeDescription')}
                  </p>
                </div>
                <Switch />
              </div>
            </CardContent>
          </Card>

          {/* Save Settings */}
          <div className="flex justify-end">
            <Button size="lg">{t('common.saveAllSettings')}</Button>
          </div>
        </div>
      </div>
    </Dashboard>
  );
};

export default Settings;