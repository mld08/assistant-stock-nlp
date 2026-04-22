import './ResultTable.css';

const ResultTable = ({ data, columns }) => {
  if (!data || data.length === 0) return null;

  const displayColumns = columns || Object.keys(data[0]);

  const formatValue = (value, column) => {
    if (value === null || value === undefined || value === '') return '—';
    
    if (typeof value === 'number') {
      if (column === 'CUMP' || column === 'TOTAL' || column === 'FAS à appliquer') {
        return new Intl.NumberFormat('fr-FR', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        }).format(value);
      }
      return new Intl.NumberFormat('fr-FR').format(value);
    }
    
    return String(value);
  };

  const getColumnLabel = (col) => {
    const labels = {
      'Article': '📦 Article',
      'Description': '📝 Description',
      'TOTAL': '📊 Total',
      'CUMP': '💰 CUMP',
      'FAS à appliquer': '📋 FAS',
      'Famille': '👨‍👩‍👧‍👦 Famille',
    };
    return labels[col] || col;
  };

  return (
    <div className="result-table-wrapper">
      <div className="result-table-header">
        <span className="result-count">{data.length} résultat{data.length > 1 ? 's' : ''}</span>
      </div>
      <div className="result-table-scroll">
        <table className="result-table">
          <thead>
            <tr>
              {displayColumns.map((col, idx) => (
                <th key={idx}>{getColumnLabel(col)}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, rowIdx) => (
              <tr key={rowIdx} style={{ animationDelay: `${rowIdx * 0.05}s` }}>
                {displayColumns.map((col, colIdx) => (
                  <td key={colIdx} data-label={col}>
                    {formatValue(row[col], col)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ResultTable;
