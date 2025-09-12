/**
 * Hook for detecting multi-agent mode on application startup
 */

import { ipcBridge } from '@/common';
import { Message } from '@arco-design/web-react';
import React, { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

export const useMultiAgentDetection = () => {
  const { t } = useTranslation();
  const [message, contextHolder] = Message.useMessage();

  useEffect(() => {
    const checkMultiAgentMode = async () => {
      try {
        const response = await ipcBridge.acpConversation.getAvailableAgents.invoke();
        if (response && response.success && response.data) {
          // 检测是否有多个ACP智能体（不包括内置的Gemini）
          const acpAgents = response.data.filter((agent: { backend: string; name: string; cliPath?: string }) => agent.backend !== 'gemini');
          if (acpAgents.length > 1) {
            message.success({
              content: (
                <div style={{ lineHeight: '1.5' }}>
                  <div>{t('conversation.welcome.multiAgentModeEnabled')}</div>
                </div>
              ),
              duration: 0,
              showIcon: true,
              className: 'aion-multi-agent-message',
              style: {
                position: 'fixed',
                top: '40px',
                left: '50%',
                transform: 'translateX(-50%)',
                zIndex: 1050,
                maxWidth: '340px',
                width: 'fit-content',
                background: 'linear-gradient(to right, #e8ffea 0%, #f5ffe8 100%)',
                border: '1px solid var(--color-border-2, rgba(229, 230, 235, 1))',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
                fontWeight: 500,
                padding: '14px 20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              },
            });
          }
        }
      } catch (error) {
        // 静默处理错误，避免影响应用启动
        console.log('Multi-agent detection failed:', error);
      }
    };

    checkMultiAgentMode();
  }, []); // 空依赖数组确保只在组件初始化时执行一次

  return { contextHolder };
};
