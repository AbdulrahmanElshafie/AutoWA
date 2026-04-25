# To Do

*Note: For deeper technical rules on each component, refer to the local `README.md` file found inside every module directory (e.g., `gui/README.md`, `core/README.md`, `app/README.md`).*

## Bugs & Fixes
1. If a bug required the app to close and open wa it screws the rest => attempted
2. Save progress on cancel or exit => attempted
3. Image cropper should work by clicking and holding while drawing the box, not two separate clicks
4. Icons preview should not scale images when selected
5. Split Save/Crop btn into two: Crop (saves cropped image into object) and Save (writes image file to disk)
6. Limit icon search area to the designated screen region to avoid false matches from taskbar or bookmarks bar icons
7. Recent alerts section should expand to show error details when an alert is clicked

## Minor Features
1. Handle nums that're already created
2. Improve the continue progress sheet
3. Save last used wa account and switch regardless if stops 

## Major Features
1. Icon capture & management => In Progress.
2. Sending locations, emojis, and richer WhatsApp interactions.
3. Turning the system into a WhatsApp customer support agent.
4. Adding support for foreign phone numbers (non-Egyptian) instead of directly texting them.
5. Add support for additional languages and light mode styling. (By mapping secondary assets and configuration fallbacks)

## Major Changes

# Done - Changlelog
v2.1.0 Beta
1. App Modularization: Decoupled GUI into `gui/layout.py` & `gui/events.py` => Done 
2. JSONL Structured Logging: Added to core engine for robust parsing => Done
3. Analytics Module: Session-based throughput metrics integrated => Done
4. System health and error logs stats monitoring and management dashboard & error alarm system => Done (Now decoupled under `monitoring/` and `analytics/` processing JSONL telemetry)

v1.1.0
1. Fix nums w WA and not sent - avg => Done
2. Fix num not deleted - minor => Done
3. Add WA business assets => Done
4. UI stability detection => Done

v1.2.0
1. Allow script to send permits and seglat in one sheet by adding a type field => Done

v1.3.0
1. In the results popup show a stats for the progress (sent, pending, not sent) => Done
2. Progress and timing popup => Done

v1.3.1
1. If a bug required the app to close and open wa it screws the rest => attempted
2. Save progress on cancel or exit => attempted
3. If start with some field not valid disable btns regardless => Done
4. Start when all done triggers pause => Done

v1.4.0
1. Auto switch language to English => Done

v1.5.0 Alpha
1. Icon capture

v1.5.1 Alpha
1. Fix icon capture
2. Fix break popup 