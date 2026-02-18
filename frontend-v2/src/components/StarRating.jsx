import { useState } from 'react';
import Icons from './Icons';

/**
 * Reusable interactive star-rating selector.
 *
 * Props:
 *   value     – current selected rating (0 = none)
 *   onChange  – (newValue) => void
 *   size      – icon pixel size (default 32)
 *   disabled  – read-only mode
 *   readOnly  – alias for disabled
 */
function StarRating({ value = 0, onChange, size = 32, disabled = false, readOnly = false }) {
  const [hover, setHover] = useState(0);
  const isReadOnly = disabled || readOnly;

  return (
    <div style={{ display: 'inline-flex', gap: '4px' }}>
      {[1, 2, 3, 4, 5].map((star) => {
        const filled = star <= (hover || value);
        return (
          <span
            key={star}
            onMouseEnter={() => !isReadOnly && setHover(star)}
            onMouseLeave={() => !isReadOnly && setHover(0)}
            onClick={() => !isReadOnly && onChange?.(star)}
            style={{ cursor: isReadOnly ? 'default' : 'pointer', lineHeight: 0 }}
          >
            {filled ? (
              <Icons.StarFilled size={size} color="#fbbf24" />
            ) : (
              <Icons.Star size={size} color="#d1d5db" />
            )}
          </span>
        );
      })}
    </div>
  );
}

export default StarRating;
