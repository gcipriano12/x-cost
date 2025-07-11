
import React, { useState } from 'react';
import Dashboard from '@/components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { Key, Plus, TestTube, Edit, Trash2, Info } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { useCredentials } from '@/hooks/useCredentials';
import { AWSCredentials, CredentialsResponse } from '@/types/api';
import { AccessPattern, CredentialType, EnhancedValidationResult } from '@/types/credentials';
import { useForm } from 'react-hook-form';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import AccessPatternSelector from '@/components/credentials/AccessPatternSelector';
import RoleConfiguration from '@/components/credentials/RoleConfiguration';
import CredentialValidation from '@/components/credentials/CredentialValidation';

const AWS_REGIONS = [
  'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
  'eu-central-1', 'eu-west-1', 'eu-west-2', 'eu-west-3',
  'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1',
  'sa-east-1', 'ca-central-1'
];

const Credentials = () => {
  const { credentials, loading, createCredential, updateCredential, deleteCredential, testCredential } = useCredentials();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingCredential, setEditingCredential] = useState<string | null>(null);
  
  // Estados para sistema dual de credenciais
  const [accessPattern, setAccessPattern] = useState<AccessPattern>(AccessPattern.HYBRID);
  const [credentialType, setCredentialType] = useState<CredentialType>(CredentialType.PROGRAMMATIC);
  const [roleConfig, setRoleConfig] = useState({
    useRoles: false,
    dataRoleArn: '',
    apiRoleArn: '',
    externalId: '',
    managedIdentityId: ''
  });
  const [validationResult, setValidationResult] = useState<EnhancedValidationResult | null>(null);
  const [isValidating, setIsValidating] = useState(false);

  const form = useForm<Omit<AWSCredentials, 'id'>>({
    defaultValues: {
      name: '',
      aws_access_key_id: '',
      aws_secret_access_key: '',
      aws_region: '',
      is_active: true,
    },
  });

  // Função de validação estendida
  const handleEnhancedValidation = async (credentialId?: string) => {
    if (!credentialId) return;
    
    setIsValidating(true);
    try {
      const response = await fetch(`/api/v1/credentials/${credentialId}/enhanced-test`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) throw new Error('Validation failed');
      
      const result = await response.json();
      setValidationResult(result);
      return result;
    } catch (error) {
      console.error('Enhanced validation error:', error);
      throw error;
    } finally {
      setIsValidating(false);
    }
  };

  const onSubmit = async (data: Omit<AWSCredentials, 'id'>) => {
    try {
      // Preparar dados estendidos mantendo compatibilidade
      const submitData = {
        ...data,
        // Adicionar campos estendidos
        access_pattern: accessPattern,
        credential_type: roleConfig.useRoles ? CredentialType.ROLE_BASED : CredentialType.PROGRAMMATIC,
        data_role_arn: roleConfig.dataRoleArn,
        api_role_arn: roleConfig.apiRoleArn,
        external_id: roleConfig.externalId,
        use_roles: roleConfig.useRoles
      };
      
      if (editingCredential) {
        await updateCredential(editingCredential, submitData);
      } else {
        await createCredential(submitData);
      }
      setDialogOpen(false);
      setEditingCredential(null);
      form.reset();
      // Reset estados dos novos campos
      setAccessPattern(AccessPattern.HYBRID);
      setRoleConfig({ useRoles: false, dataRoleArn: '', apiRoleArn: '', externalId: '', managedIdentityId: '' });
      setValidationResult(null);
    } catch (error) {
      console.error('Error saving credential:', error);
    }
  };

  const handleEdit = (credential: CredentialsResponse) => {
    setEditingCredential(credential.id);
    form.reset({
      name: credential.name,
      aws_access_key_id: '',
      aws_secret_access_key: '',
      aws_region: credential.region_preference || credential.aws_region || '',
      is_active: credential.status === 'active',
    });
    
    // Carregar dados estendidos se existirem
    if (credential.access_pattern) {
      setAccessPattern(credential.access_pattern);
    }
    if (credential.use_roles) {
      setRoleConfig({
        useRoles: credential.use_roles,
        dataRoleArn: credential.data_role_arn || '',
        apiRoleArn: credential.api_role_arn || '',
        externalId: credential.external_id || '',
        managedIdentityId: ''
      });
    }
    
    setDialogOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this credential?')) {
      await deleteCredential(id);
    }
  };

  const handleTest = async (id: string) => {
    await testCredential(id);
  };

  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <PageHeader 
          icon={Key} 
          title="AWS Credentials" 
          color="text-green-600"
          actions={
            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
              <DialogTrigger asChild>
                <Button onClick={() => {
                  setEditingCredential(null);
                  form.reset();
                  setAccessPattern(AccessPattern.HYBRID);
                  setRoleConfig({ useRoles: false, dataRoleArn: '', apiRoleArn: '', externalId: '', managedIdentityId: '' });
                  setValidationResult(null);
                }}>
                  <Plus className="mr-2 h-4 w-4" />
                  Add Credential
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>
                    {editingCredential ? 'Edit AWS Credential' : 'Add AWS Credential'}
                  </DialogTitle>
                  <DialogDescription>
                    Configure your AWS credentials with enhanced access patterns for secure and flexible cost analysis.
                  </DialogDescription>
                </DialogHeader>
                <Form {...form}>
                  <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                    <FormField
                      control={form.control}
                      name="name"
                      rules={{ required: 'Name is required' }}
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Name</FormLabel>
                          <FormControl>
                            <Input placeholder="My AWS Account" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="aws_access_key_id"
                      rules={{ required: 'Access Key ID is required' }}
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>AWS Access Key ID</FormLabel>
                          <FormControl>
                            <Input placeholder="AKIA..." {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="aws_secret_access_key"
                      rules={{ required: 'Secret Access Key is required' }}
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>AWS Secret Access Key</FormLabel>
                          <FormControl>
                            <Input type="password" placeholder="Secret key..." {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="aws_region"
                      rules={{ required: 'Region is required' }}
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>AWS Region</FormLabel>
                          <Select onValueChange={field.onChange} value={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select region" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {AWS_REGIONS.map((region) => (
                                <SelectItem key={region} value={region}>
                                  {region}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    {/* Seletor de padrão de acesso - NOVO */}
                    <div className="space-y-4">
                      <AccessPatternSelector
                        value={accessPattern}
                        onChange={setAccessPattern}
                        provider="AWS"
                        disabled={loading}
                      />
                    </div>
                    
                    {/* Configuração de roles - NOVO */}
                    <div className="space-y-4">
                      <RoleConfiguration
                        provider="AWS"
                        accessPattern={accessPattern}
                        value={roleConfig}
                        onChange={setRoleConfig}
                      />
                    </div>
                    
                    {/* Nota sobre uso híbrido */}
                    {roleConfig.useRoles && accessPattern === AccessPattern.HYBRID && (
                      <Alert>
                        <Info className="h-4 w-4" />
                        <AlertDescription>
                          No modo híbrido, as credenciais programáticas serão usadas para assumir roles 
                          e acessar APIs que não suportam role-based access.
                        </AlertDescription>
                      </Alert>
                    )}
                    
                    {/* Validação aprimorada - NOVO */}
                    {editingCredential && (
                      <div className="space-y-4">
                        <CredentialValidation
                          credentialId={editingCredential.toString()}
                          accessPattern={accessPattern}
                          onValidate={handleEnhancedValidation}
                          isValidating={isValidating}
                          validationResult={validationResult}
                        />
                      </div>
                    )}
                    
                    <div className="flex justify-end space-x-2 pt-4">
                      <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                        Cancel
                      </Button>
                      <Button type="submit" disabled={loading}>
                        {editingCredential ? 'Update' : 'Create'}
                      </Button>
                    </div>
                  </form>
                </Form>
              </DialogContent>
            </Dialog>
          }
        />
        
        <div className="p-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg font-medium">Configured Credentials</CardTitle>
            </CardHeader>
            <CardContent>
              {credentials.length === 0 ? (
                <div className="text-center py-8">
                  <Key className="mx-auto h-12 w-12 text-muted-foreground" />
                  <h3 className="mt-2 text-sm font-semibold text-muted-foreground">No credentials</h3>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Add your first AWS credential to start analyzing costs.
                  </p>
                </div>
              ) : (
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Region</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Created</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {credentials.map((credential) => (
                        <TableRow key={credential.id}>
                          <TableCell className="font-medium">{credential.name}</TableCell>
                          <TableCell>{credential.region_preference || credential.aws_region || '-'}</TableCell>
                          <TableCell>
                            <Badge variant={credential.status === 'active' ? 'default' : 'secondary'}>
                              {credential.status === 'active' ? 'Active' : 'Inactive'}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            {new Date(credential.created_at).toLocaleDateString()}
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex justify-end space-x-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleTest(credential.id)}
                                disabled={loading}
                              >
                                <TestTube className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleEdit(credential)}
                              >
                                <Edit className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleDelete(credential.id)}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </Dashboard>
  );
};

export default Credentials;
