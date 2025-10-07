# AI Shopping Assistant - React Frontend

This is a React-based frontend for the AI Shopping Assistant, refactored from the original HTML implementation.

## Features

- Modern React with TypeScript
- Responsive chat interface
- Real-time messaging with the backend API
- Session management
- Loading states and error handling

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Project Structure

```
src/
├── components/
│   ├── ChatContainer.tsx    # Main chat container with state management
│   ├── ChatHeader.tsx       # Chat header component
│   ├── ChatMessages.tsx     # Messages display container
│   ├── Message.tsx          # Individual message component
│   ├── LoadingIndicator.tsx # Loading state component
│   └── ChatInput.tsx        # Message input component
├── types.ts                 # TypeScript type definitions
├── App.tsx                  # Main App component
├── main.tsx                 # Application entry point
└── index.css                # Global styles

```

## Backend Integration

The frontend connects to the backend API at `http://localhost:8001/query`. Make sure the backend server is running before starting the frontend.

## Component Architecture

- **ChatContainer**: Main component managing chat state, messages, and API calls
- **ChatMessages**: Renders the list of messages with scroll management
- **Message**: Individual message component with user/agent styling
- **ChatInput**: Input component with send functionality
- **ChatHeader**: Static header with title and description
- **LoadingIndicator**: Shows loading state during API calls