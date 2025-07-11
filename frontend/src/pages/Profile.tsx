import React from 'react';
import Dashboard from '@/components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { UserCircle, Mail, Shield, Clock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Avatar, AvatarFallback, AvatarInitials } from '@/components/ui/avatar';
import { useAuth } from '@/hooks/useAuth';
import { useTranslation } from 'react-i18next';

const Profile = () => {
  const { user } = useAuth();
  const { t } = useTranslation();

  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <PageHeader 
          icon={UserCircle} 
          title={t('common.profileInformation')} 
          color="text-blue-600"
        />
        
        <div className="p-4 space-y-6">
          {/* Profile Information Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UserCircle className="h-5 w-5" />
                {t('common.profileInformation')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Avatar Section */}
              <div className="flex items-center gap-4">
                <Avatar className="h-20 w-20">
                  <AvatarFallback className="text-lg">
                    {user?.username?.slice(0, 2).toUpperCase() || 'SF'}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <h3 className="text-lg font-semibold">{user?.username || 'svc_finops'}</h3>
                  <p className="text-muted-foreground">{user?.role || 'finops_admin'}</p>
                  <Button variant="outline" size="sm" className="mt-2">
                    {t('common.changeAvatar')}
                  </Button>
                </div>
              </div>

              {/* Form Fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="username">{t('common.username')}</Label>
                  <Input 
                    id="username" 
                    value={user?.username || 'svc_finops'} 
                    disabled 
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="email">{t('common.email')}</Label>
                  <Input 
                    id="email" 
                    type="email" 
                    value={user?.email || 'finops@company.com'} 
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="role">{t('common.role')}</Label>
                  <Input 
                    id="role" 
                    value={user?.role || 'finops_admin'} 
                    disabled 
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="created">{t('common.memberSince')}</Label>
                  <Input 
                    id="created" 
                    value={user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'June 14, 2025'} 
                    disabled 
                  />
                </div>
              </div>

              <div className="flex justify-end">
                <Button>{t('common.updateProfile')}</Button>
              </div>
            </CardContent>
          </Card>

          {/* Account Security Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                {t('common.accountSecurity')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <h4 className="font-medium">{t('common.password')}</h4>
                  <p className="text-sm text-muted-foreground">{t('common.lastChanged')}</p>
                </div>
                <Button variant="outline">{t('common.changePassword')}</Button>
              </div>
              
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <h4 className="font-medium">{t('common.twoFactorAuth')}</h4>
                  <p className="text-sm text-muted-foreground">{t('common.twoFactorDescription')}</p>
                </div>
                <Button variant="outline">{t('common.enable2FA')}</Button>
              </div>
            </CardContent>
          </Card>

          {/* Activity Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                {t('common.recentActivity')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center gap-3 p-3 border rounded-lg">
                  <div className="h-2 w-2 bg-green-500 rounded-full"></div>
                  <div>
                    <p className="text-sm font-medium">{t('common.loggedIn')}</p>
                    <p className="text-xs text-muted-foreground">Today at {new Date().toLocaleTimeString()}</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 p-3 border rounded-lg">
                  <div className="h-2 w-2 bg-blue-500 rounded-full"></div>
                  <div>
                    <p className="text-sm font-medium">{t('common.profileUpdated')}</p>
                    <p className="text-xs text-muted-foreground">2 days ago</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 p-3 border rounded-lg">
                  <div className="h-2 w-2 bg-orange-500 rounded-full"></div>
                  <div>
                    <p className="text-sm font-medium">{t('common.passwordChanged')}</p>
                    <p className="text-xs text-muted-foreground">30 days ago</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </Dashboard>
  );
};

export default Profile;