# Force Creator
A tool for making force lists for the tabletop game Blood &amp; Plunder by Firelock Games.

## Goal
The Blood & Plunder Force Creator is intended as an improvement on and alternative to the currently available tool, the Force Builder.

## User Demographics
The Blood & Plunder Force Creator is for anyone who plays or might be interested in playing Blood & Plunder by Firelock Games.

## Data
Most if not all necessary data can be obtained from the current Force Builder. Additional data from official Firelock sources as well as third-party sources will be added manually as needed. A local API will be created to provide this data for the front-end.

## Features and Improvements
The Force Creator will retain the current features of the Force Builder to aid the user in creating valid force lists for Blood & Plunder, as well as storage and print-formatting of lists. The Force Creator will build on this functionality with the following improvements:
- Provide an option for a comprehensive (relevant) rules reference for a given list (only partially supported by Force Builder).
- Complete functionality for user selections and choices. Some user selections impact other selection options and all such outcomes should be site-automated (only partially automated by Force Builder).
- Complete and accurate rendering of units including modifications made by user selections and including any data not present in Force Builder such as sidearms.
- Additional user filters such as limiting force options to specified historical ranges or supplements.
- Provide assignment functionality including unit assignments for characters as well as actual unit assignments. Units and artillery may be assigned to specific ship decks.

## User Flow
1. Force list may optionally be assigned a name and the point total may be changed (defaults to 150).
2. User selects Nationality.
   - Front-end checks session storage for Commander and Faction options for that Nationality.
   - If not already present in session, complete Commander and Faction options for the selected Nationality are retrieved via API call and then stored in the session.
   - Commander and Faction lists are generated from session data and the dropdowns are populated.
3. User selects Commander and Faction from interdependent lists.
   - Data retrieved from session.
   - When user changes the value of either dropdown the other dropdown will be reset. If a valid option was present in other dropdown it will be automatically selected.
4. User adds elements to their list and modifies those elements as desired based upon provided options. Elements may be added and modified in any order. Elements include units, artillery, characters, ships, terrain, and misc. Points (x / Total) will be updated live based on selections and modifications.
   - Lists of all elements other than units may be obtained from the API as soon as a Commander and Faction have been selected.
   - Unit options will vary based on Commander and Faction selections. The number of API calls used to obtain these lists and how much data is transferred in each will be decided later.
   - Data will be stored in the session.
5. User may save/share their list by generating a url that re-creates it. Alternately, account functionality may be added with list-save functionality.
6. User may create a PDF of their list for printing and/or local storage. User options for the PDF will include ability and/or weapons and equipment rules references.

## Further Potential Features and Improvements

### Additional Force Creator Features
- Alternate Layout: Option for traditional Force Builder layout.
- Content Creator Links: A list of links to third-party content generated dynamically based upon user selection.
- Ship GUI: An interface that displays a ship hull for each ship in a list, demarcated by deck. Units may be assigned to decks and moved around via drag-and-drop.

### Additional Force Builder Features
- The Force Builder has the option for logging in via the user’s Facebook or Google account. This may be added to Force Creator based on user feedback.
- The Force Builder has the option to add all necessary products for a list to a cart in the Firelock webstore. This feature is not currently planned for implementation.

### Game Manager
- Used to plan/schedule a game with another user.
  - Potential user flow:
    - First user sets game parameters as desired. Parameters include date, time, location, game type (land/sea/amphibious), point total, and scenario. Some parameters will have the option for randomization.
    - When parameters are set the first user submits a “challenge” to a second (specified) user. The second user is notified of the challenge and its parameters via email or otherwise.
    - The second user may accept or deny the challenge, or may modify it and issue it back to the first user.
    - Users may optionally be sent one or more reminder notifications prior to their scheduled game. Notifications may include reminders to make a force list for the game or just that the game is coming up.
- Additional potential features:
  - Users may submit their force list for the game. If both users submit a force list additional features may be implemented.
  - Force lists will optionally be made visible to both users along with the game parameters.
  - Attacker will be automatically/randomly determined if desired by users, incorporating any relevant bonuses from the force lists (faction abilities).
  - A game specific chat room/log for pre-game communication and trash talk.

### Personal Collection Showcase
- Create Collection Units to reflect owned models and store them on the user account.
- Collection Units may be named and given other properties such as quantity and the units that the Collection Unit can be used for in force lists.
- Collection Units may include an image gallery (user uploads), one image from which may be selected as the Collection Unit’s icon.

### Additional Community Features
- A local discussion board with shared user accounts.
- A geographically based player/opponent locator that users may opt into.
- Rate-My-List feature where users may provide feedback on other users’ force lists.
