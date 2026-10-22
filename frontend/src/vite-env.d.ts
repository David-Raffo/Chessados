/// <reference types="vite/client" />

// Elemento <piece> de chessground, usado fuera del tablero para pintar piezas capturadas
declare namespace JSX {
  interface IntrinsicElements {
    piece: React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
  }
}
