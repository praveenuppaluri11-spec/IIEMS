# modules/utils.py

def format_indian_currency(value, use_shorthand=True, include_symbol=True):
    """
    Formats a numeric value into the Indian currency system.
    If use_shorthand is True, it converts to 'Lakhs' or 'Crores'.
    If False, it uses traditional Indian comma grouping (e.g., 1,50,00,000).
    """
    symbol = "₹" if include_symbol else ""
    
    if value is None:
        return f"{symbol}0"
        
    try:
        value = float(value)
    except (ValueError, TypeError):
        return f"{symbol}0"
        
    is_negative = value < 0
    value = abs(value)
    
    if use_shorthand:
        # Shorthand text notation
        if value >= 1_00_00_000:  # 1 Crore
            formatted = f"{value / 1_00_00_000:,.2f} Crores"
        elif value >= 1_00_000:   # 1 Lakh
            formatted = f"{value / 1_00_000:,.2f} Lakhs"
        else:
            # Below 1 Lakh, just use the exact number
            formatted = f"{value:,.0f}"
    else:
        # Strict Indian Comma Notation (e.g., 1,50,25,000)
        val_str = str(int(round(value)))
        if len(val_str) > 3:
            last_three = val_str[-3:]
            other_digits = val_str[:-3]
            # Group the remaining digits by 2s (Indian style)
            other_digits = ','.join([other_digits[max(0, i-2):i] for i in range(len(other_digits), 0, -2)][::-1])
            formatted = f"{other_digits},{last_three}"
        else:
            formatted = f"{val_str}"
            
    final_str = f"{symbol}{formatted}"
    return f"-{final_str}" if is_negative else final_str