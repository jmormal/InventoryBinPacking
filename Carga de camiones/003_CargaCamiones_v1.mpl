TITLE  
    PlanificacionTransporte;

OPTIONS
    DatabaseType=Access
    DatabaseAccess="Transporte_cubicaje.mdb"

INDEX
    i    := DATABASE("Productos", "IdProducto");
    i'	 := DATABASE("Productos", "IdProducto2");
    f	 := DATABASE("Familias", "IdFamilia");
    c    := DATABASE("Camiones", "IdCamion" WHERE "IdCamion"<4);
    t    := DATABASE("Dias", "IdDia" WHERE "IdDia"<=12);
    t'   := DATABASE("Dias", "IdDia");

    

DATA

    LotePedido[f]    		:=DATABASE("Familias", "LotePedido");
    PiezasCont[i]		:=DATABASE("Productos", "PiezasCont");
    b[i,f]			:=DATABASE("beta","beta");
    StockInicial[i]		:=DATABASE("Productos", "StockInicial");
    Demanda[i,t']		:=DATABASE("Demanda", "Demanda"); 
    Valor[i]			:=DATABASE("Productos", "Valor")
    PC[c]			:=(1000,1000,1000,1000,1000); !Penalización Uso de Camion
    
    L				:=30;		! maxima capacidad de contenedores por camión

!************************************* Limites a configurar ***********************************************   
    nu				:=26/30;        ! minima proporción de camión ocupado 
    NT_lw			:=5;		! low limit number trucks
    NT_up			:=10;		!upper limit number trucks 
    
VARIABLES


	
    CantidadPedir[i,c,t] -> CPICT
       EXPORT REFILL TO DATABASE("CantidadPedir", "CP");
    
    CantidadPedir2[i,f,c,t]-> CPICT2
       EXPORT REFILL TO DATABASE("CantidadPedir2", "CP2");

    ContenedoresCamion[c,t]->CC;

    Stock[i,t] -> STID
	EXPORT REFILL TO DATABASE("Stock", "ST");

    RetrasoDemanda[i,t] -> RDID
   	EXPORT REFILL TO DATABASE("Retraso", "Rd");

    K[f,c,t] -> KICT
	EXPORT REFILL TO DATABASE("K", "K");


    Y[c,t] -> YCT
	EXPORT REFILL TO DATABASE("Y", "Y");

    u;

MACROS

   UsoCamion := SUM(c,t:L*Y)-SUM(c,t:ContenedoresCamion);
   CTransporte:= SUM(c,t:PC*Y);
   !ValorStock:= SUM(i,t:Valor*Stock[i,t])/12;
   NumeroCamiones:= SUM(c,t:Y);
   !RFuzzy2		:= NT_up-u*(NT_up-NT_lw);
  

MODEL

Min Z= CTransporte;


SUBJECT TO

     RStock[i,t=1] -> RSTID : Stock[i,t] = StockInicial[i] - Demanda[i,t':=1]  + SUM(c: CantidadPedir[i,c,t]);
     RStock[i,t>1] -> RSTID : Stock[i,t] = Stock[i,t-1] - Demanda[i,t':=t] + SUM(c: CantidadPedir[i,c,t]);

     RCantidadPedir2[i,f,c,t] -> RCPICT : CantidadPedir2[i,f,c,t]= K*LotePedido*b;
	RCantidadPedir[i,c,t] -> RCPICT : CantidadPedir[i,c,t]= SUM(f:CantidadPedir2[i,f,c,t]);

  
     RContenedores[c,t]-> RCC: ContenedoresCamion[c,t]= SUM(i: CantidadPedir/PiezasCont);

     RDimensionesCamion[c,t] -> RDC : ContenedoresCamion<=L*Y[c,t];

     RLlenado[c,t]: ContenedoresCamion>=L*nu*Y[c,t];
     RCoberturaStock[i,t] -> RCB2: Stock[i,t]>=0.4*Demanda[i,t':=t+1];

     !RFuzzyOb2: NumeroCamiones 		<= NT_up-u*(NT_up-NT_lw);

BOUNDS

    Stock[i,t]>=0;
     u>=0;
     u<=1;
    

INTEGER

    K[f,c,t];
    CantidadPedir2[i,f,c,t];
    ContenedoresCamion[c,t];

BINARY

    Y[c,t];

END
   

