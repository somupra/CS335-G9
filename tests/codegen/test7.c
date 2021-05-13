int sum(int a, int b){
	int i ;
	i = a + b ;
	return i ;
}

int mult(int a, int b){
	int i ; 
	i = a*b ;
	return i ;
}


int main(){
	int x = 9 ;
	int y = 11 ;
	int z, w ;
	z = sum(x, y) ;
	w = mult(x, y) ;
	return 0 ;
}
