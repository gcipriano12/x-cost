import React, { useState, useRef, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { MessageCircle, X, Send, Bot } from "lucide-react";
import { useTheme } from "@/hooks/useTheme";
import { cn } from "@/lib/utils";

interface Message {
  text: string;
  isUser: boolean;
  timestamp: Date;
}

// Função para gerar um ID único para a sessão de chat
const generateChatId = () => {
  return 'chat_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
};

// Função para formatar texto como tabela HTML quando detectar padrão de tabela
const formatMessageText = (text: string): React.ReactNode => {
  // Verifica se o texto contém padrões de tabela (linhas com vários |)
  if (text.includes('|') && text.split('\n').filter(line => line.includes('|')).length > 1) {
    const lines = text.split('\n');
    const tableLines: string[] = [];
    const otherLines: string[] = [];
    
    let inTable = false;
    let tableHTML = '';
    
    // Separar linhas de tabela de outro conteúdo
    lines.forEach(line => {
      // Linhas com pelo menos 2 pipes são consideradas parte da tabela
      if (line.trim().includes('|') && (line.match(/\|/g) || []).length >= 2) {
        if (!inTable) {
          inTable = true;
          tableHTML = '<table className="border-collapse w-full my-2">';
        }
        
        // Processar a linha como parte da tabela
        const isHeader = line.includes('---') || line.includes('===');
        if (!isHeader) {
          tableHTML += '<tr>';
          const cells = line.split('|').filter(cell => cell.trim() !== '');
          cells.forEach(cell => {
            // Processar formatação Markdown dentro das células da tabela
            let cellContent = cell.trim();
            cellContent = cellContent.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            cellContent = cellContent.replace(/\*(.*?)\*/g, '<em>$1</em>');
            
            tableHTML += `<td className="border border-slate-300 dark:border-slate-700 px-2 py-1">${cellContent}</td>`;
          });
          tableHTML += '</tr>';
        }
      } else {
        if (inTable) {
          inTable = false;
          tableHTML += '</table>';
          otherLines.push(tableHTML);
          tableHTML = '';
        }
        otherLines.push(line);
      }
    });
    
    // Fechar a tabela se ainda estiver aberta
    if (inTable) {
      tableHTML += '</table>';
      otherLines.push(tableHTML);
    }
    
    // Converter as linhas restantes em elementos React
    return (
      <div>
        {otherLines.map((line, index) => {
          if (line.startsWith('<table')) {
            return (
              <div 
                key={index} 
                dangerouslySetInnerHTML={{ __html: line }} 
                className="overflow-x-auto my-2"
              />
            );
          }
          
          // Processar formatação Markdown básica no texto normal
          let processedLine = line;
          processedLine = processedLine.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
          processedLine = processedLine.replace(/\*(.*?)\*/g, '<em>$1</em>');
          
          if (processedLine.includes('<strong>') || processedLine.includes('<em>')) {
            return <p key={index} dangerouslySetInnerHTML={{ __html: processedLine }} />;
          }
          
          return <p key={index}>{processedLine}</p>;
        })}
      </div>
    );
  }
  
  // Processar formatação Markdown básica no texto quando não há tabela
  let processedText = text;
  processedText = processedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  processedText = processedText.replace(/\*(.*?)\*/g, '<em>$1</em>');
  
  if (processedText.includes('<strong>') || processedText.includes('<em>')) {
    return <div dangerouslySetInnerHTML={{ __html: processedText }} />;
  }
  
  // Retornar o texto normal se não tiver formatação especial
  return text;
};

export function ChatBot() {
  const { isDark } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [chatId, setChatId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Gerar um novo chatId quando o chat é aberto pela primeira vez
  useEffect(() => {
    if (isOpen && !chatId) {
      setChatId(generateChatId());
    }
  }, [isOpen, chatId]);

  // Esta função rola a área de mensagens para a mensagem mais recente
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Efeito para rolagem automática quando as mensagens são atualizadas ou o carregamento muda
  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Formatar mensagens anteriores para o contexto
  const formatPreviousMessages = () => {
    // Encontrar a última mensagem do usuário
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].isUser) {
        return [{
          text: messages[i].text,
          isUser: true,
          timestamp: messages[i].timestamp.toISOString()
        }];
      }
    }
    return []; // Retorna array vazio se não encontrar mensagem do usuário
  };

  // Função para extrair a resposta do formato retornado pelo webhook
  const extractResponse = (data: any): string => {
    // Se a resposta for um array e tiver pelo menos um elemento
    if (Array.isArray(data) && data.length > 0) {
      // Verifica se o primeiro elemento tem a propriedade 'output'
      if (data[0] && data[0].output) {
        return data[0].output;
      }
    }
    
    // Verifica se data é um objeto com a propriedade 'output' diretamente
    if (data && data.output) {
      return data.output;
    }
    
    // Formatos alternativos
    if (data && data.response) {
      return data.response;
    }
    
    // Formato não reconhecido, retorna mensagem padrão
    console.warn('Formato de resposta não reconhecido:', data);
    return 'Desculpe, não consegui processar sua mensagem.';
  };

  const sendMessage = async () => {
    if (!message.trim()) return;

    const newMessage: Message = {
      text: message,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, newMessage]);
    setMessage('');
    setIsLoading(true);

    // Garantir que tenhamos um chatId válido
    const currentChatId = chatId || generateChatId();
    if (!chatId) {
      setChatId(currentChatId);
    }

    try {
      const response = await fetch('https://vreco.app.n8n.cloud/webhook/chatbot', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: newMessage.text,
          chatId: currentChatId,
          previous_messages: formatPreviousMessages()
        }),
      });

      if (!response.ok) {
        throw new Error('Falha ao enviar mensagem');
      }

      const data = await response.json();
      
      // Usar a função extractResponse para obter o texto da resposta
      const responseText = extractResponse(data);
      
      setMessages(prev => [...prev, {
        text: responseText,
        isUser: false,
        timestamp: new Date()
      }]);
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      setMessages(prev => [...prev, {
        text: 'Desculpe, ocorreu um erro ao processar sua mensagem.',
        isUser: false,
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Reset do chat quando é fechado
  const handleCloseChat = () => {
    setIsOpen(false);
    // Opcional: Deixar o histórico e o chatId persistir entre aberturas
    // Se quiser limpar o histórico ao fechar, descomente as linhas abaixo:
    // setMessages([]);
    // setChatId(null);
  };

  return (
    <>
      {/* Botão flutuante do chat */}
      <Button
        className="fixed bottom-4 right-4 rounded-full w-12 h-12 p-0 bg-XCost-blue hover:bg-XCost-blue/90"
        onClick={() => setIsOpen(prev => !prev)}
      >
        <MessageCircle className="h-6 w-6" />
      </Button>

      {/* Modal do chat */}
      {isOpen && (
        <div className="fixed bottom-20 right-4 w-80 z-50">
          <Card className={cn(
            "w-full shadow-lg",
            isDark ? "bg-slate-800 border-slate-700" : "bg-white"
          )}>
            {/* Header do chat */}
            <div className={cn(
              "flex items-center justify-between p-4 border-b",
              isDark ? "border-slate-700" : "border-gray-200"
            )}>
              <div className="flex items-center">
                <Bot className={cn(
                  "h-5 w-5 mr-2",
                  isDark ? "text-blue-400" : "text-XCost-blue"
                )} />
                <h3 className={cn(
                  "font-semibold",
                  isDark ? "text-white" : "text-gray-900"
                )}>FinBot Assistant</h3>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={handleCloseChat}
                className={isDark ? "text-gray-300 hover:text-white" : ""}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>

            {/* Área de mensagens */}
            <div className={cn(
              "h-96 overflow-y-auto p-4 space-y-4",
              isDark ? "bg-slate-900" : "bg-gray-50"
            )}>
              {messages.length === 0 ? (
                <div className={cn(
                  "h-full flex flex-col items-center justify-center text-center p-4",
                  isDark ? "text-slate-400" : "text-slate-500"
                )}>
                  <Bot className={cn(
                    "h-12 w-12 mb-4",
                    isDark ? "text-slate-600" : "text-slate-300"
                  )} />
                  <p className="text-sm mb-2">Como posso ajudar você hoje?</p>
                  <p className="text-xs">Faça uma pergunta sobre custos de nuvem, orçamentos ou recomendações de economia.</p>
                </div>
              ) : (
                messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-2 ${
                        msg.isUser
                          ? 'bg-XCost-blue text-white'
                          : isDark 
                            ? 'bg-slate-800 text-gray-100' 
                            : 'bg-white text-gray-900 border border-gray-200'
                      }`}
                    >
                      {msg.isUser ? (
                        <p className="text-sm">{msg.text}</p>
                      ) : (
                        <div className="text-sm whitespace-pre-wrap">
                          {formatMessageText(msg.text)}
                        </div>
                      )}
                      <span className={cn(
                        "text-xs opacity-70",
                        isDark && !msg.isUser ? "text-gray-400" : ""
                      )}>
                        {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>
                ))
              )}
              {isLoading && (
                <div className="flex justify-start">
                  <div className={cn(
                    "rounded-lg p-2",
                    isDark 
                      ? "bg-slate-800 border border-slate-700"
                      : "bg-white border border-gray-200"
                  )}>
                    <p className={cn(
                      "text-sm",
                      isDark ? "text-gray-300" : "text-gray-700"
                    )}>
                      Pensando...
                    </p>
                  </div>
                </div>
              )}
              {/* Elemento de referência para rolagem automática */}
              <div ref={messagesEndRef} />
            </div>

            {/* Input de mensagem */}
            <div className={cn(
              "p-4 border-t",
              isDark ? "border-slate-700 bg-slate-800" : "border-gray-200"
            )}>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  sendMessage();
                }}
                className="flex gap-2"
              >
                <Input
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Digite sua mensagem..."
                  className={cn(
                    "flex-1",
                    isDark 
                      ? "bg-slate-700 border-slate-600 text-white placeholder:text-gray-400" 
                      : ""
                  )}
                />
                <Button
                  type="submit"
                  disabled={isLoading || !message.trim()}
                  className="bg-XCost-blue hover:bg-XCost-blue/90"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </form>
            </div>
          </Card>
        </div>
      )}
    </>
  );
} 