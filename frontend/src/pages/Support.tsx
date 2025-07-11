import React, { useState } from 'react';
import Dashboard from '@/components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { HelpCircle, MessageSquare, FileText, ExternalLink, Search, Send } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { useTranslation } from 'react-i18next';

const Support = () => {
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');
  const [ticketForm, setTicketForm] = useState({
    subject: '',
    category: '',
    priority: '',
    description: ''
  });

  const faqItems = [
    {
      question: "How do I add AWS credentials?",
      answer: "Go to My Account > Credentials and click 'Add Credential' to configure your AWS access.",
      category: "Credentials"
    },
    {
      question: "Why are my costs showing as $0?",
      answer: "This usually means credentials haven't been validated or billing data isn't available yet.",
      category: "Data"
    },
    {
      question: "How to set up budget alerts?",
      answer: "Navigate to Budgets page and create a new budget with alert thresholds.",
      category: "Budgets"
    },
    {
      question: "Can I export cost reports?",
      answer: "Yes, go to Reports page and use the export functionality for CSV or PDF downloads.",
      category: "Reports"
    }
  ];

  const handleSubmitTicket = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle ticket submission
    console.log('Ticket submitted:', ticketForm);
  };

  const filteredFAQ = faqItems.filter(item => 
    item.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.answer.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <PageHeader 
          icon={HelpCircle} 
          title="Support" 
          color="text-purple-600"
        />
        
        <div className="p-4 space-y-6">
          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="cursor-pointer hover:shadow-md transition-shadow">
              <CardContent className="p-6 text-center">
                <MessageSquare className="h-8 w-8 mx-auto mb-2 text-blue-500" />
                <h3 className="font-semibold mb-1">{t('common.liveChat')}</h3>
                <p className="text-sm text-muted-foreground">{t('common.liveChatDescription')}</p>
                <Button className="mt-3" size="sm">{t('common.startChat')}</Button>
              </CardContent>
            </Card>
            
            <Card className="cursor-pointer hover:shadow-md transition-shadow">
              <CardContent className="p-6 text-center">
                <FileText className="h-8 w-8 mx-auto mb-2 text-green-500" />
                <h3 className="font-semibold mb-1">{t('common.documentation')}</h3>
                <p className="text-sm text-muted-foreground">{t('common.documentationDescription')}</p>
                <Button variant="outline" className="mt-3" size="sm">
                  <ExternalLink className="h-4 w-4 mr-1" />
                  {t('common.viewDocs')}
                </Button>
              </CardContent>
            </Card>
            
            <Card className="cursor-pointer hover:shadow-md transition-shadow">
              <CardContent className="p-6 text-center">
                <HelpCircle className="h-8 w-8 mx-auto mb-2 text-orange-500" />
                <h3 className="font-semibold mb-1">{t('common.community')}</h3>
                <p className="text-sm text-muted-foreground">{t('common.communityDescription')}</p>
                <Button variant="outline" className="mt-3" size="sm">
                  <ExternalLink className="h-4 w-4 mr-1" />
                  {t('common.joinForum')}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* FAQ Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="h-5 w-5" />
                {t('common.faq')}
              </CardTitle>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder={t('common.searchFAQ')}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {filteredFAQ.map((item, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <div className="flex-1">
                        <h4 className="font-medium mb-2 flex items-center gap-2">
                          {item.question}
                          <Badge variant="secondary" className="text-xs">
                            {item.category}
                          </Badge>
                        </h4>
                        <p className="text-sm text-muted-foreground">{item.answer}</p>
                      </div>
                    </div>
                  </div>
                ))}
                {filteredFAQ.length === 0 && (
                  <p className="text-center text-muted-foreground py-8">
                    No FAQ items found matching your search.
                  </p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Contact Support */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                {t('common.contactSupport')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmitTicket} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="subject">{t('common.subject')}</Label>
                    <Input
                      id="subject"
                      placeholder={t('common.subjectPlaceholder')}
                      value={ticketForm.subject}
                      onChange={(e) => setTicketForm(prev => ({ ...prev, subject: e.target.value }))}
                      required
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="category">{t('common.category')}</Label>
                    <Select 
                      value={ticketForm.category} 
                      onValueChange={(value) => setTicketForm(prev => ({ ...prev, category: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder={t('common.selectCategory')} />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="credentials">Credentials</SelectItem>
                        <SelectItem value="data">Data Issues</SelectItem>
                        <SelectItem value="budgets">Budgets</SelectItem>
                        <SelectItem value="reports">Reports</SelectItem>
                        <SelectItem value="billing">Billing</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="priority">{t('common.priority')}</Label>
                  <Select 
                    value={ticketForm.priority} 
                    onValueChange={(value) => setTicketForm(prev => ({ ...prev, priority: value }))}
                  >
                    <SelectTrigger className="w-full md:w-48">
                      <SelectValue placeholder={t('common.selectPriority')} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="urgent">Urgent</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="description">{t('common.description')}</Label>
                  <Textarea
                    id="description"
                    placeholder={t('common.descriptionPlaceholder')}
                    rows={5}
                    value={ticketForm.description}
                    onChange={(e) => setTicketForm(prev => ({ ...prev, description: e.target.value }))}
                    required
                  />
                </div>
                
                <div className="flex justify-end">
                  <Button type="submit" className="flex items-center gap-2">
                    <Send className="h-4 w-4" />
                    {t('common.submitTicket')}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          {/* Contact Information */}
          <Card>
            <CardHeader>
              <CardTitle>{t('common.otherWaysToReach')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-2">{t('common.emailSupport')}</h4>
                  <p className="text-sm text-muted-foreground mb-1">support@xcost.com</p>
                  <p className="text-xs text-muted-foreground">{t('common.emailResponseTime')}</p>
                </div>
                
                <div>
                  <h4 className="font-semibold mb-2">{t('common.phoneSupport')}</h4>
                  <p className="text-sm text-muted-foreground mb-1">+1 (555) 123-4567</p>
                  <p className="text-xs text-muted-foreground">{t('common.phoneHours')}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </Dashboard>
  );
};

export default Support;