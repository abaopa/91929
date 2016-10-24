VERSION 5.00
Begin VB.Form MyCardTable 
   BackColor       =   &H00FF0000&
   BorderStyle     =   3  'Fixed Dialog
   Caption         =   "9, 19, 29"
   ClientHeight    =   3375
   ClientLeft      =   525
   ClientTop       =   1815
   ClientWidth     =   6585
   LinkTopic       =   "Form1"
   MaxButton       =   0   'False
   MinButton       =   0   'False
   ScaleHeight     =   3375
   ScaleWidth      =   6585
   ShowInTaskbar   =   0   'False
   Begin VB.PictureBox NextCard 
      BackColor       =   &H00FF0000&
      BorderStyle     =   0  'None
      Height          =   1455
      Left            =   5400
      ScaleHeight     =   1455
      ScaleWidth      =   1215
      TabIndex        =   10
      Top             =   360
      Width           =   1215
   End
   Begin VB.CommandButton BtnDeal 
      Caption         =   "Deal"
      Height          =   975
      Left            =   5400
      TabIndex        =   4
      Top             =   2280
      Width           =   1095
   End
   Begin VB.PictureBox Deck3 
      BackColor       =   &H00FF0000&
      BorderStyle     =   0  'None
      Height          =   2895
      Left            =   4080
      ScaleHeight     =   2895
      ScaleWidth      =   1215
      TabIndex        =   3
      Top             =   360
      Width           =   1215
   End
   Begin VB.PictureBox Deck2 
      BackColor       =   &H00FF0000&
      BorderStyle     =   0  'None
      Height          =   2895
      Left            =   2760
      ScaleHeight     =   2895
      ScaleWidth      =   1215
      TabIndex        =   2
      Top             =   360
      Width           =   1215
   End
   Begin VB.PictureBox Deck1 
      BackColor       =   &H00FF0000&
      BorderStyle     =   0  'None
      Height          =   2895
      Left            =   1440
      ScaleHeight     =   2895
      ScaleWidth      =   1215
      TabIndex        =   1
      Top             =   360
      Width           =   1215
   End
   Begin VB.PictureBox Deck0 
      BackColor       =   &H00FF0000&
      BorderStyle     =   0  'None
      Height          =   2895
      Left            =   120
      ScaleHeight     =   2895
      ScaleWidth      =   1215
      TabIndex        =   0
      Top             =   360
      Width           =   1215
   End
   Begin VB.Label LabelDealCnt 
      Alignment       =   2  'Center
      BackColor       =   &H8000000E&
      Caption         =   "0"
      Height          =   255
      Left            =   5400
      TabIndex        =   11
      Top             =   120
      Width           =   1095
   End
   Begin VB.Label LabelFree 
      Alignment       =   2  'Center
      Caption         =   "0"
      Height          =   255
      Left            =   5400
      TabIndex        =   9
      Top             =   1920
      Width           =   1095
   End
   Begin VB.Label Label3 
      Alignment       =   2  'Center
      Caption         =   "0"
      Height          =   255
      Left            =   4080
      TabIndex        =   8
      Top             =   120
      Width           =   1095
   End
   Begin VB.Label Label2 
      Alignment       =   2  'Center
      Caption         =   "0"
      Height          =   255
      Left            =   2760
      TabIndex        =   7
      Top             =   120
      Width           =   1095
   End
   Begin VB.Label Label1 
      Alignment       =   2  'Center
      Caption         =   "0"
      Height          =   255
      Left            =   1440
      TabIndex        =   6
      Top             =   120
      Width           =   1095
   End
   Begin VB.Label Label0 
      Alignment       =   2  'Center
      Caption         =   "0"
      Height          =   255
      Left            =   120
      TabIndex        =   5
      Top             =   120
      Width           =   1095
   End
   Begin VB.Menu mnuGame 
      Caption         =   "&Game"
      Begin VB.Menu mnuNew 
         Caption         =   "&New Game"
         Shortcut        =   {F2}
      End
      Begin VB.Menu mnuReplay 
         Caption         =   "&Replay"
         Shortcut        =   {F3}
      End
      Begin VB.Menu mnuSep2 
         Caption         =   "-"
      End
      Begin VB.Menu mnuSave 
         Caption         =   "&Save Game"
      End
      Begin VB.Menu mnuLoad 
         Caption         =   "&Load Game"
      End
      Begin VB.Menu mnuSep 
         Caption         =   "-"
      End
      Begin VB.Menu mnuExit 
         Caption         =   "E&xit"
      End
   End
   Begin VB.Menu mnuOptions 
      Caption         =   "&Options"
      Begin VB.Menu mnuPeepNext 
         Caption         =   "&Peep Next"
      End
      Begin VB.Menu mnuAutoCheck 
         Caption         =   "&Auto Check"
      End
      Begin VB.Menu mnuWarning 
         Caption         =   "&Warning"
      End
      Begin VB.Menu mnuAutoRun 
         Caption         =   "Auto &Run"
      End
   End
   Begin VB.Menu mnuHelp 
      Caption         =   "&Help"
      Begin VB.Menu mnuAbout 
         Caption         =   "&About 9, 19, 29"
      End
   End
End
Attribute VB_Name = "MyCardTable"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Private Type DeckInfo
    hDC As Long
    nCardCount As Integer
    bDeckEmpty As Integer
    rgDeck(40) As Integer
End Type

Private Type CardQueue
    nCount As Integer
    nHead As Integer
    nTail As Integer
    rgDeck(40) As Integer
End Type

Dim Deck(4) As DeckInfo
Dim CardQ As CardQueue

Dim bAutoRun As Integer
Dim bGameInitialized As Integer
Dim bAutoCheck As Integer
Dim bPeepNext As Integer
Dim bWarning As Integer
Dim bWin As Integer
Dim nDeal As Integer
Dim dxCard As Long, dyCard As Long
Dim nDeckCurrent As Integer
Dim dwX As Long, dwY As Long

Sub Form_Load()
    mnuSave.Enabled = False
    mnuReplay.Enabled = False
    mnuAutoRun.Checked = False
    bAutoRun = False
    mnuAutoCheck.Checked = False
    bAutoCheck = False
    mnuPeepNext.Checked = False
    bPeepNext = False
    mnuWarning.Checked = False
    bWarning = False
    BtnDeal.Enabled = False
    bGameInitialized = False
    InitDeck
    x% = cdtInit(dxCard, dyCard)
    dwX = 0
End Sub

Sub Form_Unload(Cancel As Integer)
    cdtTerm
End Sub

Private Sub Deck0_DblClick()
    If CollectThreeCard(0) = False Then
        If bWarning Then Beep
    Else
        RePaintDeck (0)
    End If
End Sub

Private Sub Deck1_DblClick()
    If CollectThreeCard(1) = False Then
        If bWarning Then Beep
    Else
        RePaintDeck (1)
    End If
End Sub

Private Sub Deck2_DblClick()
    If CollectThreeCard(2) = False Then
        If bWarning Then Beep
    Else
        RePaintDeck (2)
    End If
End Sub

Private Sub Deck3_DblClick()
    If CollectThreeCard(3) = False Then
        If bWarning Then Beep
    Else
        RePaintDeck (3)
    End If
End Sub

Private Sub mnuAutoCheck_Click()
    mnuAutoCheck.Checked = Not mnuAutoCheck.Checked
    bAutoCheck = mnuAutoCheck.Checked
End Sub

Private Sub mnuAutoRun_Click()
    mnuAutoRun.Checked = Not mnuAutoRun.Checked
    bAutoRun = mnuAutoRun.Checked
End Sub

Private Sub mnuLoad_Click()
    Open "card.txt" For Input As #1    ' Open file for output.
    For i = 0 To 51
        Input #1, rgDeck(i)
    Next i
    Close #1    ' Close file.
    BtnDeal.Enabled = True
    bGameInitialized = True
    nDeckCurrent = 0
'   ShuffleDeck
    InitialDeckInfo
    CardQueueInit
    ' remove Jacks, Queens, Kings
    For i = 0 To 51
        If rgDeck(i) < 40 Then
            PutCardIntoQueue (rgDeck(i))
        End If
    Next i
    
    NextCard.Cls
    bWin = False
    nDeal = 0
    LabelDealCnt.Caption = nDeal
    LabelDealCnt.Refresh

    ' PreDeal 12 cards for 4 decks
    For i = 0 To 11
        DealOneCard
    Next i
    LabelFree.Caption = CardQ.nCount
    LabelFree.Refresh
End Sub

Private Sub mnuPeepNext_Click()
    mnuPeepNext.Checked = Not mnuPeepNext.Checked
    bPeepNext = mnuPeepNext.Checked
    NextCard.Cls
End Sub

Private Sub mnuExit_Click()
    Unload MyCardTable
End Sub


Private Sub mnuSave_Click()
    Open "card.txt" For Output As #1    ' Open file for output.
    For i = 0 To 51
        Write #1, rgDeck(i);
    Next i
    Close #1    ' Close file.
End Sub

Private Sub mnuWarning_Click()
    mnuWarning.Checked = Not mnuWarning.Checked
    bWarning = mnuWarning.Checked
End Sub

Private Sub mnuReplay_Click()
    ReplayDeck40
    NextCard.Cls
    bWin = False
    nDeal = 0
    LabelDealCnt.Caption = nDeal
    LabelDealCnt.Refresh
    ' PreDeal 12 cards for 4 decks
    For i = 0 To 11
        DealOneCard
    Next i
    LabelFree.Caption = CardQ.nCount
    LabelFree.Refresh

End Sub

Private Sub mnuNew_Click()
    mnuSave.Enabled = True
    mnuReplay.Enabled = True
    ShuffleDeck40
    NextCard.Cls
    bWin = False
    nDeal = 0
    ' PreDeal 12 cards for 4 decks
    For i = 0 To 11
        DealOneCard
    Next i
    LabelFree.Caption = CardQ.nCount
    LabelFree.Refresh
    If bAutoRun Then
        While Not bWin And CardQ.nCount And Not CardQueueEmpty() And nDeal < 1000
            DealOneCard
        Wend
        LabelDealCnt.Caption = nDeal
        LabelDealCnt.Refresh
    End If
End Sub

Private Sub BtnDeal_Click()
    If bAutoRun Then
        While Not bWin And CardQ.nCount And Not CardQueueEmpty() And nDeal < 1000
            DealOneCard
        Wend
        LabelDealCnt.Caption = nDeal
        LabelDealCnt.Refresh
    Else
        DealOneCard
    End If
    LabelFree.Caption = CardQ.nCount
    LabelFree.Refresh
    If CardQ.nCount = 0 Then
        bGameInitialized = False
        BtnDeal.Enabled = False
    End If
End Sub

Sub ShuffleDeck40()
    BtnDeal.Enabled = True
    bGameInitialized = True
    nDeckCurrent = 0
    ShuffleDeck
    InitialDeckInfo
    CardQueueInit
    ' remove Jacks, Queens, Kings
    For i = 0 To 51
        If rgDeck(i) < 40 Then
            PutCardIntoQueue (rgDeck(i))
        End If
    Next i
End Sub

Sub InitialDeckInfo()
    For i = 0 To 3
        Select Case i
        Case 1
            Deck(i).hDC = Deck1.hDC
        Case 2
            Deck(i).hDC = Deck2.hDC
        Case 3
            Deck(i).hDC = Deck3.hDC
        Case Else
            Deck(i).hDC = Deck0.hDC
        End Select
        Deck(i).bDeckEmpty = False
        Deck(i).nCardCount = 0
    Next i
End Sub

Sub DealOneCard()
    If bGameInitialized And bWin <> True Then
        i = nDeckCurrent
        If Deck(i).bDeckEmpty = True Then
            i = i + 1
            i = i Mod 4
            While Deck(i).bDeckEmpty = True And i <> nDeckCurrent
                i = i + 1
                i = i Mod 4
            Wend
        End If
        If bAutoCheck Then
            If FCollectCards(0) = True Then
                CollectThreeCard (0)   ' Cheating
                If bWarning Then Beep
            End If
            If FCollectCards(1) = True Then
                CollectThreeCard (1)   ' Cheating
                If bWarning Then Beep
            End If
            If FCollectCards(2) = True Then
                CollectThreeCard (2)   ' Cheating
                If bWarning Then Beep
            End If
            If FCollectCards(3) = True Then
                CollectThreeCard (3)   ' Cheating
                If bWarning Then Beep
            End If
        End If
        If Not bWin Then
            Deck(i).rgDeck(Deck(i).nCardCount) = GetCardFromQueue
            nDeal = nDeal + 1
            LabelDealCnt.Caption = nDeal
            LabelDealCnt.Refresh
        
            'dwY = Deck(i).nCardCount * dyCard / 5
            'ret% = cdtDraw(Deck(i).hDC, dwX, dwY, Deck(i).rgDeck(Deck(i).nCardCount), mdFaceUp, &HFFFFFF)
        
            Deck(i).nCardCount = Deck(i).nCardCount + 1
            RePaintDeck (i)
        
            nDeckCurrent = i + 1
            nDeckCurrent = nDeckCurrent Mod 4
            If bPeepNext Then
                ret% = cdtDraw(NextCard.hDC, dwX, 0, PeekCardFromQueue, mdFaceUp, &HFFFFFF)
            End If
        End If
    End If
End Sub

Function CollectThreeCard(nDeck As Integer) As Integer
    CollectThreeCard = False
    If Deck(nDeck).bDeckEmpty <> True Then
        If Deck(nDeck).nCardCount >= 3 Then
            nSumT12B1 = Int(Deck(nDeck).rgDeck(0) / 4) + Int(Deck(nDeck).rgDeck(1) / 4) + Int(Deck(nDeck).rgDeck(Deck(nDeck).nCardCount - 1) / 4) + 3
            nSumT1B12 = Int(Deck(nDeck).rgDeck(0) / 4) + Int(Deck(nDeck).rgDeck(Deck(nDeck).nCardCount - 2) / 4) + Int(Deck(nDeck).rgDeck(Deck(nDeck).nCardCount - 1) / 4) + 3
            nSumTB123 = Int(Deck(nDeck).rgDeck(Deck(nDeck).nCardCount - 3) / 4) + Int(Deck(nDeck).rgDeck(Deck(nDeck).nCardCount - 2) / 4) + Int(Deck(nDeck).rgDeck(Deck(nDeck).nCardCount - 1) / 4) + 3
            If nSumT12B1 = 9 Or nSumT12B1 = 19 Or nSumT12B1 = 29 Then
                PutCardIntoQueue (Deck(nDeck).rgDeck(0))
                PutCardIntoQueue (Deck(nDeck).rgDeck(1))
                PutCardIntoQueue (Deck(nDeck).rgDeck(Deck(nDeck).nCardCount - 1))
                Deck(nDeck).nCardCount = Deck(nDeck).nCardCount - 3
                If Deck(nDeck).nCardCount = 0 Then Deck(nDeck).bDeckEmpty = True
                CollectThreeCard = True
                For i = 0 To Deck(nDeck).nCardCount
                    Deck(nDeck).rgDeck(0 + i) = Deck(nDeck).rgDeck(2 + i)
                Next i
            ElseIf nSumT1B12 = 9 Or nSumT1B12 = 19 Or nSumT1B12 = 29 Then
                PutCardIntoQueue (Deck(nDeck).rgDeck(0))
                PutCardIntoQueue (Deck(nDeck).rgDeck(Deck(nDeck).nCardCount - 2))
                PutCardIntoQueue (Deck(nDeck).rgDeck(Deck(nDeck).nCardCount - 1))
                Deck(nDeck).nCardCount = Deck(nDeck).nCardCount - 3
                If Deck(nDeck).nCardCount = 0 Then Deck(nDeck).bDeckEmpty = True
                CollectThreeCard = True
                For i = 0 To Deck(nDeck).nCardCount
                    Deck(nDeck).rgDeck(0 + i) = Deck(nDeck).rgDeck(1 + i)
                Next i
            ElseIf nSumTB123 = 9 Or nSumTB123 = 19 Or nSumTB123 = 29 Then
                PutCardIntoQueue (Deck(nDeck).rgDeck(Deck(nDeck).nCardCount - 3))
                PutCardIntoQueue (Deck(nDeck).rgDeck(Deck(nDeck).nCardCount - 2))
                PutCardIntoQueue (Deck(nDeck).rgDeck(Deck(nDeck).nCardCount - 1))
                Deck(nDeck).nCardCount = Deck(nDeck).nCardCount - 3
                If Deck(nDeck).nCardCount = 0 Then Deck(nDeck).bDeckEmpty = True
                CollectThreeCard = True
            End If
        End If
    End If
    If bAutoCheck Then
        If CollectThreeCard = True Then
            RePaintDeck (nDeck)
            CollectThreeCard (nDeck)
        End If
    End If
    If Not bWin Then
        If Deck(0).bDeckEmpty And Deck(1).bDeckEmpty And Deck(2).bDeckEmpty And Deck(3).bDeckEmpty Then
            For i = 0 To 3
                RePaintDeck (i)
            Next i
            ret% = cdtDraw(NextCard.hDC, dwX, 0, PeekCardFromQueue, mdFaceUp, &HFFFFFF)
            'MsgBox "Win!!!"
            bWin = True
            BtnDeal.Enabled = False
        End If
    End If
    If Not bWin Then
        If Deck(0).nCardCount + Deck(1).nCardCount + Deck(2).nCardCount + Deck(3).nCardCount = 1 Then
            For i = 0 To 3
                If Deck(i).nCardCount = 1 Then
                    If Deck(i).rgDeck(0) >= 8 And Deck(i).rgDeck(0) <= 11 Then
                        ret% = cdtDraw(NextCard.hDC, dwX, 0, Deck(i).rgDeck(0), mdFaceUp, &HFFFFFF)
                        'MsgBox "Win!!!"
                        bWin = True
                        BtnDeal.Enabled = False
                    End If
                End If
            Next i
        End If
    End If
End Function

Sub CardQueueInit()
    CardQ.nHead = 0
    CardQ.nTail = 0
    CardQ.nCount = 0
End Sub

Function CardQueueEmpty() As Integer
    If CardQ.nHead = CardQ.nTail Then
        CardQueueEmpty = True
    Else
        CardQueueEmpty = False
    End If
'    If CardQueueEmpty Then
'        If CardQ.nCount Then
'            MsgBox "Error!!!"
'        End If
'    End If
End Function

Function GetCardFromQueue() As Integer
    GetCardFromQueue = CardQ.rgDeck(CardQ.nHead)
    CardQ.nHead = CardQ.nHead + 1
    CardQ.nCount = CardQ.nCount - 1
    If CardQ.nHead >= 40 Then CardQ.nHead = 0
End Function

Function PeekCardFromQueue() As Integer
    PeekCardFromQueue = CardQ.rgDeck(CardQ.nHead)
End Function

Sub PutCardIntoQueue(Card As Integer)
    CardQ.rgDeck(CardQ.nTail) = Card
    CardQ.nTail = CardQ.nTail + 1
    CardQ.nCount = CardQ.nCount + 1
    If CardQ.nTail >= 40 Then CardQ.nTail = 0
End Sub

Sub RePaintDeck(nDeck As Integer)
    LabelFree.Caption = CardQ.nCount
    LabelFree.Refresh
    Select Case nDeck
    Case 1
        Deck1.Cls
        Label1.Caption = Deck(1).nCardCount
        Label1.Refresh
    Case 2
        Deck2.Cls
        Label2.Caption = Deck(2).nCardCount
        Label2.Refresh
    Case 3
        Deck3.Cls
        Label3.Caption = Deck(3).nCardCount
        Label3.Refresh
    Case Else
        Deck0.Cls
        Label0.Caption = Deck(0).nCardCount
        Label0.Refresh
    End Select
#If 1 Then
    If Deck(nDeck).nCardCount <= 5 Then
        For i = 0 To Deck(nDeck).nCardCount - 1
            dwY = i * dyCard / 5
            ret% = cdtDraw(Deck(nDeck).hDC, dwX, dwY, Deck(nDeck).rgDeck(i), mdFaceUp, &HFFFFFF)
        Next i
    Else
        j = 0
        For i = 0 To 1
            dwY = j * dyCard / 5
            ret% = cdtDraw(Deck(nDeck).hDC, dwX, dwY, Deck(nDeck).rgDeck(i), mdFaceUp, &HFFFFFF)
            j = j + 1
        Next i
        
        dwY = j * dyCard / 5
        ret% = cdtDraw(Deck(nDeck).hDC, dwX, dwY, 0, mdGhost, &HFFFFFF)
        
        j = j + 1
        For i = Deck(nDeck).nCardCount - 3 To Deck(nDeck).nCardCount - 1
            dwY = j * dyCard / 5
            ret% = cdtDraw(Deck(nDeck).hDC, dwX, dwY, Deck(nDeck).rgDeck(i), mdFaceUp, &HFFFFFF)
            j = j + 1
        Next i
    End If
#Else
    For i = 0 To Deck(nDeck).nCardCount - 1
        dwY = i * dyCard / 5
        ret% = cdtDraw(Deck(nDeck).hDC, dwX, dwY, Deck(nDeck).rgDeck(i), mdFaceUp, &HFFFFFF)
    Next i
#End If
End Sub

Sub ReplayDeck40()
    BtnDeal.Enabled = True
    bGameInitialized = True
    nDeckCurrent = 0
    InitialDeckInfo
    CardQueueInit
    ' remove Jacks, Queens, Kings
    For i = 0 To 51
        If rgDeck(i) < 40 Then
            PutCardIntoQueue (rgDeck(i))
        End If
    Next i
End Sub

Function FCollectCards(nDeck As Integer) As Integer
    FCollectCards = False
    If Deck(nDeck).bDeckEmpty <> True Then
        If Deck(nDeck).nCardCount >= 3 Then
            nSumT12B1 = Int(Deck(nDeck).rgDeck(0) / 4) + Int(Deck(nDeck).rgDeck(1) / 4) + Int(Deck(nDeck).rgDeck(Deck(nDeck).nCardCount - 1) / 4) + 3
            nSumT1B12 = Int(Deck(nDeck).rgDeck(0) / 4) + Int(Deck(nDeck).rgDeck(Deck(nDeck).nCardCount - 2) / 4) + Int(Deck(nDeck).rgDeck(Deck(nDeck).nCardCount - 1) / 4) + 3
            nSumTB123 = Int(Deck(nDeck).rgDeck(Deck(nDeck).nCardCount - 3) / 4) + Int(Deck(nDeck).rgDeck(Deck(nDeck).nCardCount - 2) / 4) + Int(Deck(nDeck).rgDeck(Deck(nDeck).nCardCount - 1) / 4) + 3
            If nSumT12B1 = 9 Or nSumT12B1 = 19 Or nSumT12B1 = 29 Then
                FCollectCards = True
            ElseIf nSumT1B12 = 9 Or nSumT1B12 = 19 Or nSumT1B12 = 29 Then
                FCollectCards = True
            ElseIf nSumTB123 = 9 Or nSumTB123 = 19 Or nSumTB123 = 29 Then
                FCollectCards = True
            End If
        End If
    End If
End Function

