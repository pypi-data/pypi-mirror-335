
import pytest
import asyncio
from brui_core.browser.browser_manager import BrowserManager
from brui_core.browser.browser_launcher import get_chrome_pids

@pytest.fixture
async def browser_manager():
    """Provide a clean BrowserManager instance for each test"""
    manager = BrowserManager()
    yield manager
    # Cleanup
    await manager.stop_browser()
    
@pytest.mark.asyncio
async def test_browser_lifecycle_management(browser_manager):
    """Test complete browser lifecycle including launch, connect, and stop"""
    # Verify initial state
    assert not await browser_manager.is_browser_running()
    assert not browser_manager.browser_launched
    assert browser_manager.browser is None
    assert browser_manager.playwright is None
    
    # Test browser launch
    await browser_manager.ensure_browser_launched()
    assert await browser_manager.is_browser_running()
    assert browser_manager.browser_launched
    initial_processes = get_chrome_pids()
    assert initial_processes, "No Chrome processes found after launch"
    
    # Test browser connection
    browser = await browser_manager.connect_browser()
    assert browser is not None
    assert browser_manager.browser is not None
    assert browser_manager.playwright is not None
    
    # Verify no additional processes created on second connection
    browser2 = await browser_manager.connect_browser()
    assert browser2 is browser  # Should reuse existing connection
    current_processes = get_chrome_pids()
    assert len(current_processes) == len(initial_processes)
    
    # Test concurrent access
    async def connect_browser():
        return await browser_manager.connect_browser()
    
    # Create multiple concurrent connection attempts
    results = await asyncio.gather(
        *[connect_browser() for _ in range(5)]
    )
    
    # Verify all connections are the same instance
    assert all(b is browser for b in results)
    assert len(get_chrome_pids()) == len(initial_processes)
    
    # Test browser stop
    await browser_manager.stop_browser()
    assert not browser_manager.browser_launched
    assert browser_manager.browser is None
    assert browser_manager.playwright is None
    assert not await browser_manager.is_browser_running()
    assert not get_chrome_pids()
    
    # Test restart after stop
    await browser_manager.ensure_browser_launched()
    assert await browser_manager.is_browser_running()
    new_browser = await browser_manager.connect_browser()
    assert new_browser is not browser  # Should be a new instance
    
    # Test error recovery
    await browser_manager.browser.close()  # Simulate browser crash
    await asyncio.sleep(1)  # Allow time for state to update
    
    # Should recover and create new connection
    recovery_browser = await browser_manager.connect_browser()
    assert recovery_browser is not new_browser
    assert await browser_manager.is_browser_running()
    
    # Verify singleton behavior
    another_manager = BrowserManager()
    assert another_manager is browser_manager
    
    # Final cleanup
    await browser_manager.stop_browser()
    assert not get_chrome_pids()
