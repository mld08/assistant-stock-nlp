import Markdown from 'react-markdown';
import ResultTable from './ResultTable.jsx';
import Spinner from './Spinner.jsx';
import './MessageBubble.css';
import { FiUser, FiCpu } from 'react-icons/fi';

const MessageBubble = ({ message }) => {
  const { role, content, type, data, columns, isLoading } = message;
  const isUser = role === 'user';

  return (
    <div className={`message-bubble ${isUser ? 'user' : 'bot'}`}>
      <div className="message-avatar">
        {isUser ? (
          <div className="avatar avatar-user">
            <FiUser />
          </div>
        ) : (
          <div className="avatar avatar-bot">
            <FiCpu />
          </div>
        )}
      </div>
      <div className="message-content">
        <div className="message-role">
          {isUser ? 'Vous' : 'Assistant Stock'}
        </div>
        <div className="message-body">
          {isLoading ? (
            <Spinner />
          ) : (
            <>
              {content && (
                <div className="message-text">
                  <Markdown>{content}</Markdown>
                </div>
              )}
              {type === 'table' && data && data.length > 0 && (
                <ResultTable data={data} columns={columns} />
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
