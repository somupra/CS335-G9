
int main(){
	int a, b, c, d, e ;
	d = 5;
	a = 7 ;
	b = a ;
	c = 2 ;
	e = a + b%c + c*d + d*9 + a/7 ;
	if(a>b || c<d){
		printf("hello, %d, %d, %d, %d", a, b, c, d) ;
	}
	else{
		printf("%d, %d, %d, %d", a, b, c, d) ;		
	}
	return 0 ;
}
