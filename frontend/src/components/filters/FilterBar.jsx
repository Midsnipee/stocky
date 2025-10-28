function FilterBar({ filters, onChange, children }) {
  const handleChange = (filter, value) => {
    if (typeof filter.onChange === 'function') {
      filter.onChange(value);
    } else if (typeof onChange === 'function') {
      onChange(filter.name, value);
    }
  };

  return (
    <div className="filter-bar">
      {filters.map((filter) => (
        <label key={filter.name}>
          <span className="sr-only">{filter.label}</span>
          {filter.type === 'select' ? (
            <select
              value={filter.value}
              onChange={(event) => handleChange(filter, event.target.value)}
            >
              {filter.options.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          ) : (
            <input
              type="search"
              placeholder={filter.placeholder}
              value={filter.value}
              onChange={(event) => handleChange(filter, event.target.value)}
            />
          )}
        </label>
      ))}
      {children}
    </div>
  );
}

export default FilterBar;
