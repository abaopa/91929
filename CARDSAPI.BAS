Attribute VB_Name = "CardsAPI"
''*-----------------------------------------------------------------------------
'|    CARDSAPI.BAS
'|
'|    VB Declares for Cards32.dll file
'|
'|  Copyright(c) 1996 Microsoft Corporation
'-----------------------------------------------------------------------------*'
Public RA As Integer '     '* Rank *'
Public SU As Integer '     '* Suit *'
Public cd As Integer '     '* Card *'
''*-----------------------------------------------------------------------------
'| cdtDraw and cdtDrawExt mode flags
'-----------------------------------------------------------------------------*'
Public Const mdFaceUp = 0           '* Draw card face up, card to draw specified by cd *'
Public Const mdFaceDown = 1         '* Draw card face down, back specified by cd (cdFaceDownFirst..cdFaceDownLast) *'
Public Const mdHilite = 2           '* Same as FaceUp except drawn with NOTSRCCOPY mode *'
Public Const mdGhost = 3            '* Draw a ghost card -- for ace piles *'
Public Const mdRemove = 4           '* draw background specified by rgbBgnd *'
Public Const mdInvisibleGhost = 5   '* ? *'
Public Const mdDeckX = 6            '* Draw X *'
Public Const mdDeckO = 7            '* Draw O *'
''*-----------------------------------------------------------------------------
'| Suit and card indices.  Orders of BOTH are important
'-----------------------------------------------------------------------------*'
Public Const suClub = 0
Public Const suDiamond = 1
Public Const suHeart = 2
Public Const suSpade = 3
Public Const suMax = 4
Public Const suFirst = suClub

Public Const raAce = 0
Public Const raTwo = 1
Public Const raThree = 2
Public Const raFour = 3
Public Const raFive = 4
Public Const raSix = 5
Public Const raSeven = 6
Public Const raEight = 7
Public Const raNine = 8
Public Const raTen = 9
Public Const raJack = 10
Public Const raQueen = 11
Public Const raKing = 12
Public Const raMax = 13
Public Const raNil = 15
Public Const raFirst = raAce

Public Const cdAClubs = 0
Public Const cd2Clubs = 4
Public Const cd3Clubs = 8
Public Const cd4Clubs = 12
Public Const cd5Clubs = 16
Public Const cd6Clubs = 20
Public Const cd7Clubs = 24
Public Const cd8Clubs = 28
Public Const cd9Clubs = 32
Public Const cdTClubs = 36
Public Const cdJClubs = 40
Public Const cdQClubs = 44
Public Const cdKClubs = 48
Public Const cdADiamonds = 1
Public Const cd2Diamonds = 5
Public Const cd3Diamonds = 9
Public Const cd4Diamonds = 13
Public Const cd5Diamonds = 17
Public Const cd6Diamonds = 21
Public Const cd7Diamonds = 25
Public Const cd8Diamonds = 29
Public Const cd9Diamonds = 33
Public Const cdTDiamonds = 37
Public Const cdJDiamonds = 41
Public Const cdQDiamonds = 45
Public Const cdKDiamonds = 49
Public Const cdAHearts = 2
Public Const cd2Hearts = 6
Public Const cd3Hearts = 10
Public Const cd4Hearts = 14
Public Const cd5Hearts = 18
Public Const cd6Hearts = 22
Public Const cd7Hearts = 26
Public Const cd8Hearts = 30
Public Const cd9Hearts = 34
Public Const cdTHearts = 38
Public Const cdJHearts = 42
Public Const cdQHearts = 46
Public Const cdKHearts = 50
Public Const cdASpades = 3
Public Const cd2Spades = 7
Public Const cd3Spades = 11
Public Const cd4Spades = 15
Public Const cd5Spades = 19
Public Const cd6Spades = 23
Public Const cd7Spades = 27
Public Const cd8Spades = 31
Public Const cd9Spades = 35
Public Const cdTSpades = 39
Public Const cdJSpades = 43
Public Const cdQSpades = 47
Public Const cdKSpades = 51
'/*-----------------------------------------------------------------------------
'| Face down cds
'-----------------------------------------------------------------------------*/
Public Const cdFaceDown1 = 54
Public Const cdFaceDown2 = 55
Public Const cdFaceDown3 = 56
Public Const cdFaceDown4 = 57
Public Const cdFaceDown5 = 58
Public Const cdFaceDown6 = 59
Public Const cdFaceDown7 = 60
Public Const cdFaceDown8 = 61
Public Const cdFaceDown9 = 62
Public Const cdFaceDown10 = 63
Public Const cdFaceDown11 = 64
Public Const cdFaceDown12 = 65
Public Const cdFaceDownFirst = cdFaceDown1
Public Const cdFaceDownLast = cdFaceDown12

'/*-----------------------------------------------------------------------------
'|    cdtInit
'|
'|        Initialize Cards32.dll -- called once at app boot time.
'|
'|    Arguments:
'|        int FAR *pdxCard: returns card width
'|        int FAR *pdyCard: returns card height
'|
'|    Returns:
'|        TRUE if successful.
'-------------------------------------------------------------------------------*/
'BOOL _declspec(dllexport) cdtInit(int FAR *pdxCard, int FAR *pdyCard);
Declare Function cdtInit Lib "Cards32.dll" (pdxCard As Long, pdyCard As Long) As Long

'/*-----------------------------------------------------------------------------
'|    cdtDraw
'|
'|        Draw a card
'|
'|    Arguments:
'|        HDC hdc
'|        int x: upper left corner of the card
'|        int y: upper left corner of the card
'|        int cd: card to draw (depends on md)
'|        int md: mode
'|           mdFaceUp:    draw face up card (cd in cdAClubs..cdKSpades)
'|           mdFaceDown:  draw face down card (cd in cdFaceDown1..cdFaceDown12)
'|           mdHilite:    draw face up card inversely
'|           mdGhost:     draw a ghost card, cd ignored
'|           mdRemove:    draw rectangle of background color at x,y
'|           mdDeckX:     draw an X
'|           mdDeckO:     draw an O
'|        DWORD rgbBgnd: table background color (only required for mdGhost and mdRemove)
'|
'|    Returns:
'|        TRUE if successful
'-----------------------------------------------------------------------------*/
'BOOL _declspec(dllexport) cdtDraw(HDC hdc, int x, int y, int cd, int md, DWORD rgbBgnd);
Declare Function cdtDraw Lib "Cards32.dll" (ByVal hDC As Long, ByVal x As Long, ByVal y As Long, ByVal ecsCard As Long, ByVal ectDraw As Long, ByVal rgbBgnd As Long) As Long

'/*-----------------------------------------------------------------------------
'|    cdtDrawExt
'|
'|        Same as cdtDraw except will stretch the cards to an arbitray extent
'|
'|    Arguments:
'|        HDC hdc
'|        int x
'|        int y
'|        int dx
'|        int dy
'|        int cd
'|        int md
'|        DWORD rgbBgnd:
'|
'|    Returns:
'|        TRUE if successful
'-----------------------------------------------------------------------------*/
'BOOL _declspec(dllexport) cdtDrawExt(HDC hdc, int x, int y, int dx, int dy,
 '                                   int cd, int md, DWORD rgbBgnd);
Declare Function cdtDrawExt Lib "Cards32.dll" (ByVal hDC As Long, ByVal x As Long, ByVal y As Long, ByVal dx As Long, ByVal dy As Long, ByVal ecsCard As Long, ByVal ectDraw As Long, ByVal rgbBgnd As Long) As Long
 
'/*-----------------------------------------------------------------------------
'|    cdtAnimate
'|
'|        Draws the animation on a card.  Four cards support animation:
'|
'|      cd         #frames    description
'|   cdFaceDown3   4          robot meters
'|   cdFaceDown10  2          bats flapping
'|   cdFaceDown11  4          sun sticks tongue out
'|   cdFaceDown12  4          cards running up and down sleave
'|
'|    Call cdtAnimate every 250 ms for proper animation speed.
'|
'|    Arguments:
'|        HDC hdc
'|        int cd    cdFaceDown3, cdFaceDown10, cdFaceDown11 or cdFaceDown12
'|        int x:    upper left corner of card
'|        int y
'|        int ispr  sprite to draw (0..1 for cdFaceDown10, 0..3 for others)
'|
'|    Returns:
'|       TRUE if successful
'-----------------------------------------------------------------------------*/
'BOOL _declspec(dllexport) cdtAnimate(HDC hdc, int cd, int x, int y, int ispr);
Declare Function cdtAnimate Lib "Cards32.dll" (ByVal hDC As Long, ByVal ecbCardBack As Long, ByVal x As Long, ByVal y As Long, ByVal iState As Long) As Long

'/*-----------------------------------------------------------------------------
'|    cdtTerm
'|
'|        Call once at app termination
'-----------------------------------------------------------------------------*/
'VOID _declspec(dllexport) cdtTerm(VOID);
Declare Sub cdtTerm Lib "Cards32.dll" ()
