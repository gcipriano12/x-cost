import React from 'react';
import { SpendingTeamsCard } from '../components/dashboard/SpendingTeamsCard';

// Teste para verificar a exibição de dados vazios
export function TestEmptyTeamData() {
  const emptyData = [];
  const currency = '$';

  return (
    <div className="p-8 bg-gray-100 min-h-screen">
      <h1 className="text-2xl font-bold mb-6">Teste - Dados Vazios de Equipe</h1>
      
      <div className="max-w-md">
        <SpendingTeamsCard 
          categories={emptyData} 
          currency={currency}
        />
      </div>
      
      <div className="mt-8">
        <h2 className="text-lg font-semibold mb-4">Estado esperado:</h2>
        <ul className="list-disc pl-6 space-y-2">
          <li>Título "Gastos por Equipe" alinhado à esquerda</li>
          <li>Mensagem "Nenhum dado de equipe disponível"</li>
          <li>Descrição "Não foram encontrados dados de gastos para o período selecionado"</li>
          <li>Ícone de gráfico de barras</li>
          <li>Sem gráfico mockado</li>
        </ul>
      </div>
    </div>
  );
}
