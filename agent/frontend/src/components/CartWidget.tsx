import React from 'react'
import { CartWidgetData } from '../types'

interface CartWidgetProps {
  data: CartWidgetData
}

const CartWidget: React.FC<CartWidgetProps> = ({ data }) => {
  const formatPrice = (price: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(price)
  }

  return (
    <div className="cart-widget">
      <div className="cart-header">
        <h3>Cart Summary</h3>
      </div>
      <div className="cart-details">
        <div className="cart-line-item">
          <span className="cart-label">Subtotal:</span>
          <span className="cart-value">
            {formatPrice(data.subtotal_amount, data.subtotal_amount_currency_code)}
          </span>
        </div>
        {data.tax_amount !== null && (
          <div className="cart-line-item">
            <span className="cart-label">Tax:</span>
            <span className="cart-value">
              {formatPrice(data.tax_amount, data.tax_amount_currency_code)}
            </span>
          </div>
        )}
        <div className="cart-line-item cart-total">
          <span className="cart-label">Total:</span>
          <span className="cart-value">
            {formatPrice(data.total_amount, data.total_amount_currency_code)}
          </span>
        </div>
      </div>
      {data.checkout_url && (
        <div className="cart-actions">
          <a 
            href={data.checkout_url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="checkout-button"
          >
            Proceed to Checkout
          </a>
        </div>
      )}
    </div>
  )
}

export default CartWidget
