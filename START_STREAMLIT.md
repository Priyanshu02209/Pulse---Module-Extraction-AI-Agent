# How to Start Streamlit App

## Quick Start

1. **Open PowerShell** in the project directory:
   ```powershell
   cd C:\Users\win11\Desktop\Pulsegen
   ```

2. **Run Streamlit**:
   ```powershell
   python -m streamlit run src/app.py
   ```

3. **Wait for the message**: "You can now view your Streamlit app in your browser"

4. **Open your browser** and go to: `http://localhost:8501`

## If Browser Doesn't Open Automatically

1. Manually open your browser
2. Type in the address bar: `http://localhost:8501`
3. Press Enter

## Troubleshooting

### "Connection Refused" Error

**Solution 1**: Make sure Streamlit is actually running
- Check the terminal window - it should show "You can now view your Streamlit app..."
- If you see errors, read them carefully

**Solution 2**: Kill any existing processes on port 8501
```powershell
# Find process using port 8501
netstat -ano | findstr :8501

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

# Then start Streamlit again
python -m streamlit run src/app.py
```

**Solution 3**: Use a different port
```powershell
python -m streamlit run src/app.py --server.port 8502
```
Then open: `http://localhost:8502`

**Solution 4**: Check Windows Firewall
- Windows Firewall might be blocking the connection
- Try temporarily disabling firewall to test
- Or add an exception for Python

**Solution 5**: Clear browser cache
- Press `Ctrl + Shift + Delete`
- Clear cached images and files
- Try again

### Streamlit Command Not Found

Use: `python -m streamlit` instead of just `streamlit`

### Port Already in Use

```powershell
# Use different port
python -m streamlit run src/app.py --server.port 8502
```

## Keep Terminal Open

**IMPORTANT**: Keep the PowerShell terminal window open while using the app. Closing it will stop the server.

## Stop the Server

Press `Ctrl + C` in the terminal window.

