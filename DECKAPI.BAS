Attribute VB_Name = "DeckAPI"
''*-----------------------------------------------------------------------------
'|    DECKAPI.BAS
'|
'|    VB Declares for Cards32.dll file
'|
'|  Copyright(c) 1996 Microsoft Corporation
'-----------------------------------------------------------------------------*'

Global rgDeck(52) As Long

Sub InitDeck()
    For i = 0 To 51
        rgDeck(i) = i
    Next i
End Sub

Sub ShuffleDeck()
    GameNum = Timer
    Randomize GameNum
    For i = 1 To 10
        For j = 0 To 51
            k = Int((52 * Rnd))
            Temp = rgDeck(j)
            rgDeck(j) = rgDeck(k)
            rgDeck(k) = Temp
        Next j
    Next i
End Sub
