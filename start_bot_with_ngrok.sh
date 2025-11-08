#!/bin/bash
# Start bot and ngrok for local testing

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     Starting Bot with ngrok for Local Testing           ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if bot is running
if pgrep -f "python.*app.py" > /dev/null; then
    echo "✅ Bot is already running"
else
    echo "🔄 Starting bot on port 5001..."
    cd "$(dirname "$0")"
    source venv/bin/activate
    PORT=5001 python3 app.py > /tmp/telegram_bot.log 2>&1 &
    sleep 3
    echo "✅ Bot started"
fi

# Check if ngrok is running
if pgrep -f "ngrok http 5001" > /dev/null; then
    echo "✅ ngrok is already running"
    echo ""
    echo "📋 Current ngrok URL:"
    curl -s http://localhost:4040/api/tunnels | python3 -m json.tool 2>/dev/null | grep -E "(public_url|name)" | head -4
else
    echo ""
    echo "🔄 Starting ngrok tunnel..."
    ngrok http 5001 > /tmp/ngrok.log 2>&1 &
    sleep 3
    echo "✅ ngrok started"
    echo ""
    echo "📋 Getting ngrok URL..."
    sleep 2
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; data=json.load(sys.stdin); print([t['public_url'] for t in data.get('tunnels', []) if t['proto']=='https'][0] if data.get('tunnels') else '')" 2>/dev/null)
    
    if [ -n "$NGROK_URL" ]; then
        echo "✅ ngrok URL: $NGROK_URL"
        echo ""
        echo "🔄 Setting webhook to ngrok URL..."
        source venv/bin/activate
        python3 set_local_webhook.py "$NGROK_URL"
        echo ""
        echo "✅ Setup complete!"
        echo ""
        echo "📱 Now test your bot on Telegram by sending /start"
    else
        echo "⚠️  Could not get ngrok URL. Check http://localhost:4040"
    fi
fi

echo ""
echo "📝 Useful commands:"
echo "   View bot logs: tail -f /tmp/telegram_bot.log"
echo "   View ngrok: http://localhost:4040"
echo "   Stop bot: pkill -f 'python.*app.py'"
echo "   Stop ngrok: pkill ngrok"

