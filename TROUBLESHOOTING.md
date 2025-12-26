# Troubleshooting Guide

## Streamlit App Not Opening

### Issue: Website/App not opening in browser

**Solution 1: Check if Streamlit is running**
```powershell
# Check if port 8501 is in use
netstat -ano | findstr :8501
```

**Solution 2: Start Streamlit properly**
```powershell
cd C:\Users\win11\Desktop\Pulsegen
python -m streamlit run src/app.py
```

**Solution 3: Use the batch script**
```powershell
.\run_streamlit.bat
```

**Solution 4: Manually open browser**
- Streamlit should automatically open your browser
- If it doesn't, manually navigate to: `http://localhost:8501`

**Solution 5: Check for port conflicts**
If port 8501 is already in use:
```powershell
# Use a different port
python -m streamlit run src/app.py --server.port 8502
```
Then open: `http://localhost:8502`

### Issue: "streamlit is not recognized"

**Solution**: Use `python -m streamlit` instead:
```powershell
python -m streamlit run src/app.py
```

### Issue: Import errors

**Solution**: Make sure you're in the project directory:
```powershell
cd C:\Users\win11\Desktop\Pulsegen
python -m streamlit run src/app.py
```

### Issue: Module not found errors

**Solution**: Install dependencies:
```powershell
pip install -r requirements.txt
```

## Common Issues

### Port Already in Use
- Kill the process using port 8501:
  ```powershell
  # Find process ID
  netstat -ano | findstr :8501
  # Kill process (replace PID with actual process ID)
  taskkill /PID <PID> /F
  ```

### Browser Not Opening Automatically
- Manually navigate to: `http://localhost:8501`
- Check firewall settings
- Try a different browser

### App Crashes on Start
- Check Python version: `python --version` (should be 3.10+)
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
- Check for error messages in the terminal

## Getting Help

If issues persist:
1. Check the terminal output for error messages
2. Verify all dependencies are installed: `pip list`
3. Try running in a fresh terminal window
4. Check Python version compatibility

