import parse, { domToReact } from "html-react-parser"

interface WidgetRendererProps {
  html: string
  onSendMessage: (msg: string) => void
}

export function WidgetRenderer({ html, onSendMessage }: WidgetRendererProps) {
  const options = {
    replace: (domNode: any) => {
      if (domNode.name === "button" && domNode.attribs?.class?.includes("add-to-cart-btn")) {
        const title = domNode.attribs["data-title"]
        return (
          <button
            className={domNode.attribs.class}
            onClick={() => onSendMessage(`add item ${title} to cart`)}
          >
            {domToReact(domNode.children, options)}
          </button>
        )
      }
      return undefined
    },
  }

  return <div className="widgets-container">{parse(html, options)}</div>
}