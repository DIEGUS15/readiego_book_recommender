import { useState } from "react";

export default function RatingStars({ rating, onRate, readonly = false }) {
  const [hover, setHover] = useState(0);

  const handleClick = (value) => {
    if (!readonly && onRate) {
      onRate(value);
    }
  };

  return (
    <div className="flex items-center space-x-1">
      {[...Array(10)].map((_, index) => {
        const starValue = index + 1;
        return (
          <button
            key={index}
            type="button"
            onClick={() => handleClick(starValue)}
            onMouseEnter={() => !readonly && setHover(starValue)}
            onMouseLeave={() => !readonly && setHover(0)}
            disabled={readonly}
            className={`text-2xl ${readonly ? "cursor-default" : "cursor-pointer"} transition-colors`}
          >
            <span
              className={
                starValue <= (hover || rating)
                  ? "text-yellow-400"
                  : "text-gray-300"
              }
            >
              ★
            </span>
          </button>
        );
      })}
      <span className="ml-2 text-sm text-gray-600">
        {rating > 0 ? `${rating}/10` : "Sin calificar"}
      </span>
    </div>
  );
}
