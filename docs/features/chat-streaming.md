# Chat Streaming Implementation

## Overview

The chat system now supports real-time streaming responses using Server-Sent Events (SSE). This provides users with immediate visual feedback as the AI response is generated token-by-token, eliminating the need for page refreshes to see replies.

## Architecture

### Backend Implementation

#### Streaming Utility
- **Location**: `app/utils/streaming.py`
- **Purpose**: Provides utilities for generating SSE streams
- **Key Functions**:
  - `stream_response_as_sse()`: Converts response content into SSE chunks
  - `stream_error_as_sse()`: Streams error messages via SSE

#### API Endpoint
- **Endpoint**: `POST /sessions/{sessionId}/messages/stream`
- **Response Type**: `text/event-stream` (SSE)
- **Headers**:
  - `Content-Type: text/event-stream`
  - `Cache-Control: no-cache`
  - `Connection: keep-alive`
  - `Access-Control-Allow-Origin: *`

#### SSE Event Types
1. **start**: Indicates the beginning of a stream
   ```json
   data: {"type": "start", "messageId": "uuid"}
   ```

2. **token**: Contains a chunk of the response content
   ```json
   data: {"type": "token", "content": "Hello there"}
   ```

3. **end**: Marks the completion of the stream
   ```json
   data: {"type": "end", "messageId": "uuid"}
   ```

4. **error**: Indicates an error occurred during streaming
   ```json
   data: {"type": "error", "error": "Error message"}
   ```

### Frontend Implementation

#### Chat API Service
- **Location**: `src/services/chatAPI.ts`
- **Function**: `sendMessageStream()`
- **Features**:
  - Proper SSE header handling
  - Buffered parsing for incomplete chunks
  - Error handling and recovery

#### Chat Page Component
- **Location**: `src/pages/ChatPage.tsx`
- **Features**:
  - Real-time message display
  - Streaming state management
  - Automatic message refresh after streaming completion

## Implementation Details

### Backend Streaming Process

1. **Message Storage**: User message is stored immediately
2. **Response Generation**: Assistant response is generated and stored
3. **Stream Creation**: Response is split into word chunks (3 words per chunk)
4. **SSE Streaming**: Chunks are sent with 100ms delays between them

### Frontend Streaming Process

1. **Request Initiation**: User sends message via streaming endpoint
2. **Stream Parsing**: SSE events are parsed and buffered
3. **UI Updates**: Tokens are displayed as they arrive
4. **Completion Handling**: Messages are refreshed when streaming ends

## Configuration

### Streaming Parameters
- **Chunk Size**: 3 words per token
- **Delay**: 100ms between chunks
- **Buffer Size**: Dynamic based on network conditions

### Error Handling
- Network failures are caught and displayed
- Parsing errors are logged but don't break the stream
- Automatic retry logic for failed connections

## Usage Example

### Frontend
```typescript
const stream = await chatAPI.sendMessageStream(
  sessionId,
  { content: "Hello", role: "user" },
  (chunk) => {
    if (chunk.type === 'token') {
      console.log('Received token:', chunk.content);
    }
  }
);
```

### Backend
```python
async def generate_stream():
    async for chunk in stream_response_as_sse(
        response_content=response,
        message_id=message.id,
        chunk_size=3,
        delay=0.1
    ):
        yield chunk

return StreamingResponse(generate_stream(), media_type="text/event-stream")
```

## Benefits

1. **Improved User Experience**: No more page refreshes needed
2. **Real-time Feedback**: Users see responses as they're generated
3. **Better Error Handling**: Errors are displayed immediately
4. **Reduced Perceived Latency**: Streaming makes responses feel faster
5. **Professional Feel**: Similar to modern chat applications

## Troubleshooting

### Common Issues

1. **Stream Not Starting**
   - Check CORS headers
   - Verify authentication token
   - Ensure proper SSE headers are set

2. **Chunk Parsing Errors**
   - Check buffer handling in frontend
   - Verify JSON format in backend
   - Monitor network conditions

3. **Performance Issues**
   - Adjust chunk size and delay
   - Monitor server resources
   - Consider connection pooling

### Debugging

1. **Backend Logs**: Check for streaming errors
2. **Browser Console**: Monitor SSE events
3. **Network Tab**: Inspect SSE response headers
4. **Frontend Logs**: Check chunk parsing logs

## Future Enhancements

1. **Adaptive Chunking**: Dynamic chunk sizes based on content
2. **Connection Recovery**: Automatic reconnection on failures
3. **Streaming Metrics**: Performance monitoring and analytics
4. **Custom Delays**: Variable delays for different content types
5. **Bidirectional Streaming**: Support for real-time input streaming