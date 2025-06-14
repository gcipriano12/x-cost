import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ThemeToggle } from '@/components/theme/ThemeToggle';
import { Logo } from '@/components/ui/logo';
import { LanguageSwitcherDropdown } from '@/components/ui/language-switcher-dropdown';
import { BarChart3, Cloud, ShieldCheck, ArrowRight, ChevronDown, CheckCircle, BuildingIcon, Server, Globe, Coins, Settings, Activity, DollarSign, LineChart } from 'lucide-react';

// Componente de dropdown para o menu de navegação
const NavDropdown = ({ 
  title, 
  children,
  isOpen,
  onToggle
}: { 
  title: string; 
  children: React.ReactNode;
  isOpen: boolean;
  onToggle: () => void;
}) => {
  return (
    <div className="relative">
      <button 
        className="flex items-center gap-1 text-sm hover:text-XCost-blue cursor-pointer"
        onClick={onToggle}
      >
        {title}
        <ChevronDown className={`h-4 w-4 transition-transform ${isOpen ? 'transform rotate-180' : ''}`} />
      </button>
      
      {isOpen && (
        <div className="absolute mt-2 top-full left-0 bg-white dark:bg-slate-900 shadow-lg rounded-md border border-gray-200 dark:border-slate-700 min-w-[350px] z-50">
          {children}
        </div>
      )}
    </div>
  );
};

// Componente para seção do dropdown
const DropdownSection = ({ title, children }: { title: string; children: React.ReactNode }) => (
  <div className="px-4 py-3">
    <h3 className="text-xs uppercase tracking-wider font-semibold text-muted-foreground mb-3">{title}</h3>
    <div className="space-y-3">
      {children}
    </div>
  </div>
);

// Componente para item do dropdown
const DropdownItem = ({ icon, title, description, href }: { 
  icon: React.ReactNode; 
  title: string; 
  description: string;
  href: string;
}) => (
  <Link to={href} className="flex items-start p-3 hover:bg-muted rounded-md transition-colors">
    <div className="mr-3 text-XCost-blue">{icon}</div>
    <div>
      <div className="text-sm font-medium">{title}</div>
      <div className="text-xs text-muted-foreground">{description}</div>
    </div>
  </Link>
);

const Landing = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  
  // Estado para controlar qual dropdown está aberto
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);
  
  const toggleDropdown = (dropdown: string) => {
    setOpenDropdown(openDropdown === dropdown ? null : dropdown);
  };

  const handleLoginClick = () => {
    navigate('/login');
  };

  const features = [
    {
      icon: <BarChart3 className="h-10 w-10 text-XCost-blue" />,
      title: t('landing.features.analytics.title', 'Cost Analytics'),
      description: t('landing.features.analytics.description', 'Deep insights into your cloud spending across providers with trend analysis and forecasting.')
    },
    {
      icon: <Cloud className="h-10 w-10 text-XCost-blue" />,
      title: t('landing.features.optimization.title', 'Cost Optimization'),
      description: t('landing.features.optimization.description', 'Identify savings opportunities and get tailored recommendations to reduce unnecessary spending.')
    },
    {
      icon: <ShieldCheck className="h-10 w-10 text-XCost-blue" />,
      title: t('landing.features.governance.title', 'FinOps Governance'),
      description: t('landing.features.governance.description', 'Establish policies, budgets and alerts to maintain financial control of your cloud resources.')
    }
  ];

  const processSteps = [
    {
      number: '01',
      title: t('landing.process.connect.title', 'Connect Accounts'),
      description: t('landing.process.connect.description', 'Easily connect your AWS, Azure, GCP and other cloud provider accounts in minutes.')
    },
    {
      number: '02',
      title: t('landing.process.analyze.title', 'Analyze Spending'),
      description: t('landing.process.analyze.description', 'Our platform automatically analyzes your cloud spending patterns and identifies inefficiencies.')
    },
    {
      number: '03',
      title: t('landing.process.save.title', 'Save Money'),
      description: t('landing.process.save.description', 'Implement our recommendations to reduce costs while maintaining or improving your cloud performance.')
    }
  ];

  const useCases = [
    {
      icon: <BuildingIcon className="h-8 w-8 text-emerald-500" />,
      title: t('landing.useCases.enterprise.title', 'Enterprise'),
      description: t('landing.useCases.enterprise.description', 'Manage complex multi-cloud environments with consolidated billing and department-level cost allocation.')
    },
    {
      icon: <Server className="h-8 w-8 text-amber-500" />,
      title: t('landing.useCases.startups.title', 'Startups'),
      description: t('landing.useCases.startups.description', 'Optimize your cloud spending as you scale to extend your runway and focus on growth.')
    },
    {
      icon: <Globe className="h-8 w-8 text-blue-500" />,
      title: t('landing.useCases.agencies.title', 'Agencies'),
      description: t('landing.useCases.agencies.description', 'Manage client cloud costs with separate accounts and detailed reporting for client billing.')
    }
  ];

  const integrations = [
    { name: 'AWS', logo: '💻' },
    { name: 'Azure', logo: '☁️' },
    { name: 'GCP', logo: '🔍' },
    { name: 'Oracle Cloud', logo: '🚀' },
    { name: 'Slack', logo: '📱' },
    { name: 'Jira', logo: '🔄' }
  ];

  const testimonials = [
    {
      quote: t('landing.testimonials.quote1', 'X Cost helped us reduce our cloud spend by 34% in just three months while improving resource utilization.'),
      author: 'Maria Silva',
      company: 'TechCloud Inc.'
    },
    {
      quote: t('landing.testimonials.quote2', 'The anomaly detection feature saved us from a massive billing surprise last quarter. Worth every penny.'),
      author: 'Carlos Mendes',
      company: 'DataFlow Systems'
    }
  ];

  const faqs = [
    {
      question: t('landing.faq.q1', 'How long does it take to set up?'),
      answer: t('landing.faq.a1', 'Setting up takes just minutes. Connect your cloud accounts through our secure API integrations, and you\'ll start seeing insights right away.')
    },
    {
      question: t('landing.faq.q2', 'Do you support all cloud providers?'),
      answer: t('landing.faq.a2', 'We support AWS, Azure, Google Cloud, Oracle Cloud, and more. Our platform is constantly expanding to include additional providers.')
    },
    {
      question: t('landing.faq.q3', 'How much can I expect to save?'),
      answer: t('landing.faq.a3', 'On average, our customers save 23-37% on their cloud bills. Your results may vary based on your current cloud setup and optimization level.')
    },
    {
      question: t('landing.faq.q4', 'Is my data secure?'),
      answer: t('landing.faq.a4', 'Absolutely. We use industry-standard encryption and security practices. We never store your cloud credentials and only access the billing data needed for analysis.')
    },
  ];

  return (
    <div className="flex flex-col min-h-screen">
      {/* Header */}
      <header className="border-b bg-background sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center">
            <Link to="/" className="flex items-center cursor-pointer">
              <Logo />
            </Link>
          </div>
          
          {/* Menu de navegação principal com dropdowns */}
          <div className="hidden md:flex items-center space-x-6">
            {/* Dropdown Solução */}
            <NavDropdown 
              title={t('landing.nav.solution')} 
              isOpen={openDropdown === 'solution'}
              onToggle={() => toggleDropdown('solution')}
            >
              <div className="grid grid-cols-2 gap-5 p-6">
                <DropdownSection title={t('landing.nav.dropdown.mainFeatures', 'MAIN FEATURES')}>
                  <DropdownItem 
                    icon={<BarChart3 className="h-5 w-5" />} 
                    title={t('common.megabill')} 
                    description={t('landing.nav.dropdown.megabill', 'One dashboard to manage them all')}
                    href="/megabill" 
                  />
                  <DropdownItem 
                    icon={<Server className="h-5 w-5" />} 
                    title={t('common.virtualTags')} 
                    description={t('landing.nav.dropdown.virtualTags', 'FinOps cost allocation solved')}
                    href="/virtual-tags" 
                  />
                  <DropdownItem 
                    icon={<Coins className="h-5 w-5" />} 
                    title={t('landing.nav.dropdown.sharedCost', 'Shared Cost')} 
                    description={t('landing.nav.dropdown.sharedCostDesc', 'Refined reallocation of shared expenses')}
                    href="/financial-plans" 
                  />
                </DropdownSection>
                
                <DropdownSection title={t('landing.nav.dropdown.costOptimization', 'COST OPTIMIZATION')}>
                  <DropdownItem 
                    icon={<ShieldCheck className="h-5 w-5" />} 
                    title={t('common.costGuard')} 
                    description={t('landing.nav.dropdown.costGuard', 'Detect and reduce waste from day one')}
                    href="/costguard" 
                  />
                  <DropdownItem 
                    icon={<Activity className="h-5 w-5" />} 
                    title={t('landing.nav.dropdown.costGuardScans', 'CostGuard Scans')} 
                    description={t('landing.nav.dropdown.costGuardScansDesc', 'Cloud cost-saving scans')}
                    href="/costguard" 
                  />
                </DropdownSection>
              </div>
            </NavDropdown>
            
            {/* Dropdown Integrações */}
            <NavDropdown 
              title={t('landing.nav.integrations')} 
              isOpen={openDropdown === 'integrations'}
              onToggle={() => toggleDropdown('integrations')}
            >
              <div className="p-4 w-64">
                <DropdownSection title={t('landing.nav.dropdown.cloudIntegrations', 'CLOUD PROVIDERS')}>
                  <DropdownItem 
                    icon={<Cloud className="h-4 w-4" />} 
                    title="AWS" 
                    description={t('landing.nav.dropdown.aws', 'Amazon Web Services integration')}
                    href="/integrations" 
                  />
                  <DropdownItem 
                    icon={<Cloud className="h-4 w-4" />} 
                    title="Azure" 
                    description={t('landing.nav.dropdown.azure', 'Microsoft Azure integration')}
                    href="/integrations" 
                  />
                  <DropdownItem 
                    icon={<Cloud className="h-4 w-4" />} 
                    title="GCP" 
                    description={t('landing.nav.dropdown.gcp', 'Google Cloud Platform integration')}
                    href="/integrations" 
                  />
                </DropdownSection>
              </div>
            </NavDropdown>
            
            {/* Link simples Preços */}
            <Link to="/pricing" className="text-sm hover:text-XCost-blue">
              {t('landing.nav.pricing')}
            </Link>
            
            {/* Dropdown Histórias de Clientes */}
            <NavDropdown 
              title={t('landing.nav.customerStories')} 
              isOpen={openDropdown === 'customerStories'}
              onToggle={() => toggleDropdown('customerStories')}
            >
              <div className="p-4 w-64">
                <DropdownSection title={t('landing.nav.dropdown.featuredStories', 'FEATURED STORIES')}>
                  <DropdownItem 
                    icon={<BuildingIcon className="h-4 w-4" />} 
                    title="TechCloud Inc." 
                    description={t('landing.nav.dropdown.storyDesc1', '34% reduction in cloud spend')}
                    href="/stories" 
                  />
                  <DropdownItem 
                    icon={<BuildingIcon className="h-4 w-4" />} 
                    title="DataFlow Systems" 
                    description={t('landing.nav.dropdown.storyDesc2', 'Avoided billing surprises')}
                    href="/stories" 
                  />
                </DropdownSection>
              </div>
            </NavDropdown>
            
            {/* Dropdown Recursos */}
            <NavDropdown 
              title={t('landing.nav.resources')} 
              isOpen={openDropdown === 'resources'}
              onToggle={() => toggleDropdown('resources')}
            >
              <div className="p-4 w-64">
                <DropdownSection title={t('landing.nav.dropdown.resources', 'RESOURCES')}>
                  <DropdownItem 
                    icon={<DollarSign className="h-4 w-4" />} 
                    title={t('landing.nav.dropdown.blog', 'Blog')} 
                    description={t('landing.nav.dropdown.blogDesc', 'Latest insights and tips')}
                    href="/resources" 
                  />
                  <DropdownItem 
                    icon={<LineChart className="h-4 w-4" />} 
                    title={t('landing.nav.dropdown.reports', 'Reports')} 
                    description={t('landing.nav.dropdown.reportsDesc', 'Industry benchmarks and analyses')}
                    href="/reports" 
                  />
                </DropdownSection>
              </div>
            </NavDropdown>
            
            {/* Dropdown Empresa */}
            <NavDropdown 
              title={t('landing.nav.company')} 
              isOpen={openDropdown === 'company'}
              onToggle={() => toggleDropdown('company')}
            >
              <div className="p-4 w-64">
                <DropdownSection title={t('landing.nav.dropdown.company', 'COMPANY')}>
                  <DropdownItem 
                    icon={<BuildingIcon className="h-4 w-4" />} 
                    title={t('landing.nav.dropdown.about', 'About Us')} 
                    description={t('landing.nav.dropdown.aboutDesc', 'Our mission and team')}
                    href="/about" 
                  />
                  <DropdownItem 
                    icon={<Settings className="h-4 w-4" />} 
                    title={t('landing.nav.dropdown.careers', 'Careers')} 
                    description={t('landing.nav.dropdown.careersDesc', 'Join our team')}
                    href="/careers" 
                  />
                </DropdownSection>
              </div>
            </NavDropdown>
          </div>
          
          <div className="flex items-center gap-4">
            <LanguageSwitcherDropdown />
            <ThemeToggle />
            <Button 
              variant="outline"
              className="hidden md:flex"
              onClick={() => navigate('/signup')}
            >
              {t('landing.cta.bookDemo')}
            </Button>
            <Button 
              onClick={handleLoginClick} 
              className="bg-XCost-blue hover:bg-blue-700 transition-colors"
            >
              {t('landing.login', 'Login')}
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section - Removido o quadrado grande */}
      <section className="py-16 md:py-24 bg-gradient-to-b from-background to-muted relative overflow-hidden">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-48 -right-48 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>
          <div className="absolute top-1/2 -left-48 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl"></div>
        </div>
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-700 to-indigo-700 dark:from-blue-400 dark:to-indigo-400">
              {t('landing.hero.title', 'Optimize Your Cloud Costs with Precision')}
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              {t('landing.hero.subtitle', 'Get complete visibility across all your cloud providers and start saving with actionable recommendations.')}
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Button 
                size="lg" 
                className="bg-XCost-blue hover:bg-blue-700 transition-colors font-semibold text-lg px-8"
                onClick={() => navigate('/signup')}
              >
                {t('landing.cta.getStarted', 'Get Started')} <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              <Button 
                size="lg" 
                variant="outline"
                className="text-lg px-8"
              >
                {t('landing.cta.watchDemo', 'Watch Demo')}
              </Button>
            </div>
            <div className="mt-12 flex flex-wrap justify-center gap-8 text-muted-foreground">
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 mr-2 text-green-500" />
                <span>{t('landing.hero.feature1', 'No credit card required')}</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 mr-2 text-green-500" />
                <span>{t('landing.hero.feature2', '14-day free trial')}</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 mr-2 text-green-500" />
                <span>{t('landing.hero.feature3', 'Cancel anytime')}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section - Nova seção */}
      <section className="py-12 bg-background border-y">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-XCost-blue mb-2">30%</div>
              <p className="text-muted-foreground">{t('landing.stats.reduction', 'Average cost reduction')}</p>
            </div>
            <div>
              <div className="text-4xl font-bold text-XCost-blue mb-2">500+</div>
              <p className="text-muted-foreground">{t('landing.stats.companies', 'Companies optimized')}</p>
            </div>
            <div>
              <div className="text-4xl font-bold text-XCost-blue mb-2">$100M+</div>
              <p className="text-muted-foreground">{t('landing.stats.saved', 'Total cloud spend saved')}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 md:py-24 bg-background">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">{t('landing.features.title', 'Key Features')}</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              {t('landing.features.subtitle', 'Discover how X Cost helps you manage and optimize your cloud expenditure effectively.')}
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="border shadow-sm hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="mb-3">{feature.icon}</div>
                  <CardTitle>{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">{feature.description}</CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section - Nova seção */}
      <section className="py-16 md:py-24 bg-muted">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">{t('landing.process.title', 'How It Works')}</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              {t('landing.process.subtitle', 'Get started in minutes and start saving on your cloud costs')}
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {processSteps.map((step, index) => (
              <div key={index} className="relative">
                <div className="bg-background rounded-lg p-8 h-full border">
                  <div className="text-4xl font-bold text-XCost-blue/20 mb-4">{step.number}</div>
                  <h3 className="text-xl font-bold mb-3">{step.title}</h3>
                  <p className="text-muted-foreground">{step.description}</p>
                </div>
                {index < processSteps.length - 1 && (
                  <div className="hidden md:block absolute top-1/2 right-0 transform translate-x-1/2 -translate-y-1/2 z-10">
                    <ArrowRight className="h-6 w-6 text-muted-foreground/50" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases Section - Nova seção */}
      <section className="py-16 md:py-24 bg-background">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">{t('landing.useCases.title', 'For Businesses of All Sizes')}</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              {t('landing.useCases.subtitle', 'Tailored solutions for different business needs')}
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {useCases.map((useCase, index) => (
              <Card key={index} className="border shadow-sm hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="mb-3">{useCase.icon}</div>
                  <CardTitle>{useCase.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">{useCase.description}</CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Integrations Section - Nova seção */}
      <section className="py-16 md:py-24 bg-muted">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">{t('landing.integrations.title', 'Seamless Integrations')}</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              {t('landing.integrations.subtitle', 'Connect with all your favorite cloud providers and tools')}
            </p>
          </div>
          
          <div className="flex flex-wrap justify-center gap-8">
            {integrations.map((integration, index) => (
              <div key={index} className="flex flex-col items-center">
                <div className="w-16 h-16 bg-background rounded-full flex items-center justify-center text-3xl mb-2 border">
                  {integration.logo}
                </div>
                <div className="font-medium">{integration.name}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section - Nova seção */}
      <section className="py-16 md:py-24 bg-blue-500 text-white">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">{t('landing.cta.title', 'Start Optimizing Your Cloud Costs Today')}</h2>
            <p className="text-xl mb-8 text-white/80">
              {t('landing.cta.subtitle', 'Join thousands of companies that trust X Cost to manage their cloud spending')}
            </p>
            <Button 
              size="lg" 
              className="bg-white text-blue-600 hover:bg-blue-50 transition-colors font-semibold text-lg px-8"
              onClick={() => navigate('/signup')}
            >
              {t('landing.cta.getStarted', 'Get Started For Free')}
            </Button>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-16 md:py-24 bg-background">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">{t('landing.testimonials.title', 'What Our Customers Say')}</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              {t('landing.testimonials.subtitle', 'Hear from businesses that have transformed their cloud cost management')}
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-muted shadow-sm rounded-lg p-8 border">
                <blockquote className="text-lg font-medium mb-6">&ldquo;{testimonial.quote}&rdquo;</blockquote>
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-XCost-blue/20 rounded-full flex items-center justify-center text-XCost-blue font-bold">
                    {testimonial.author.charAt(0)}
                  </div>
                  <div className="ml-4">
                    <div className="font-semibold">{testimonial.author}</div>
                    <div className="text-sm text-muted-foreground">{testimonial.company}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section - Nova seção */}
      <section className="py-16 md:py-24 bg-muted">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">{t('landing.faq.title', 'Frequently Asked Questions')}</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              {t('landing.faq.subtitle', 'Got questions? We have answers')}
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-x-12 gap-y-8 max-w-4xl mx-auto">
            {faqs.map((faq, index) => (
              <div key={index}>
                <h3 className="text-xl font-bold mb-2">{faq.question}</h3>
                <p className="text-muted-foreground">{faq.answer}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-16 border-t mt-auto bg-background">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
            <div>
              <div className="mb-4">
                <Link to="/" className="flex items-center cursor-pointer">
                  <Logo />
                </Link>
              </div>
              <p className="text-muted-foreground text-sm mb-4">
                {t('landing.footer.tagline', 'Cloud cost optimization made simple and effective')}
              </p>
              <div className="flex space-x-4">
                <a href="#" className="text-muted-foreground hover:text-foreground">
                  <span className="sr-only">Twitter</span>
                  📱
                </a>
                <a href="#" className="text-muted-foreground hover:text-foreground">
                  <span className="sr-only">LinkedIn</span>
                  💼
                </a>
                <a href="#" className="text-muted-foreground hover:text-foreground">
                  <span className="sr-only">GitHub</span>
                  💻
                </a>
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">{t('landing.footer.product', 'Product')}</h3>
              <ul className="space-y-2">
                <li><Link to="#" className="text-muted-foreground hover:text-foreground">{t('landing.footer.features', 'Features')}</Link></li>
                <li><Link to="#" className="text-muted-foreground hover:text-foreground">{t('landing.footer.pricing', 'Pricing')}</Link></li>
                <li><Link to="#" className="text-muted-foreground hover:text-foreground">{t('landing.footer.integrations', 'Integrations')}</Link></li>
                <li><Link to="#" className="text-muted-foreground hover:text-foreground">{t('landing.footer.changelog', 'Changelog')}</Link></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">{t('landing.footer.company', 'Company')}</h3>
              <ul className="space-y-2">
                <li><Link to="#" className="text-muted-foreground hover:text-foreground">{t('landing.footer.about', 'About')}</Link></li>
                <li><Link to="#" className="text-muted-foreground hover:text-foreground">{t('landing.footer.careers', 'Careers')}</Link></li>
                <li><Link to="#" className="text-muted-foreground hover:text-foreground">{t('landing.footer.contact', 'Contact')}</Link></li>
                <li><Link to="#" className="text-muted-foreground hover:text-foreground">{t('landing.footer.blog', 'Blog')}</Link></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">{t('landing.footer.legal', 'Legal')}</h3>
              <ul className="space-y-2">
                <li><Link to="/privacy" className="text-muted-foreground hover:text-foreground">{t('landing.footer.privacyPolicy', 'Privacy Policy')}</Link></li>
                <li><Link to="/terms" className="text-muted-foreground hover:text-foreground">{t('landing.footer.termsOfService', 'Terms of Service')}</Link></li>
                <li><Link to="#" className="text-muted-foreground hover:text-foreground">{t('landing.footer.security', 'Security')}</Link></li>
                <li><Link to="#" className="text-muted-foreground hover:text-foreground">{t('landing.footer.gdpr', 'GDPR')}</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t pt-8">
            <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
              <p className="text-muted-foreground text-sm text-center">
                {t('landing.footer.copyright', '© 2025 X Cost. All rights reserved.')}
              </p>
              <LanguageSwitcherDropdown variant="outline" size="sm" />
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
