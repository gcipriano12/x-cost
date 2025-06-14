
import { useEffect, useState } from "react"

export function useIsMobile() {
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    // Função para verificar se é mobile baseado no tamanho da tela
    const checkIsMobile = () => {
      setIsMobile(window.innerWidth <= 768)
    }
    
    // Verificar inicialmente
    checkIsMobile()
    
    // Adicionar listeners para redimensionamento e mudança de orientação
    window.addEventListener("resize", checkIsMobile)
    window.addEventListener("orientationchange", checkIsMobile)
    
    // Verificar também após um pequeno atraso para garantir a interpretação correta
    // após mudanças de orientação
    const orientationTimer = setTimeout(() => {
      checkIsMobile()
    }, 300)
    
    // Limpar listeners quando componente desmontar
    return () => {
      window.removeEventListener("resize", checkIsMobile)
      window.removeEventListener("orientationchange", checkIsMobile)
      clearTimeout(orientationTimer)
    }
  }, [])

  return isMobile
} 
