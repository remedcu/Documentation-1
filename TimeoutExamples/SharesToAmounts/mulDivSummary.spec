
// A restriction on the value of f = x * y / z
// The ratio between x (or y) and z is a rational number a/b or b/a.
// Important : do not set a = 0 or b = 0.
// Note: constRatio(x,y,z,a,b,f) <=> constRatio(x,y,z,b,a,f)
definition constRatio(uint256 x, uint256 y, uint256 z,
 uint256 a, uint256 b, uint256 f) 
        returns bool = 
        ( a * x == b * z && to_mathint(f) == (b * y) / a ) || 
        ( b * x == a * z && to_mathint(f) == (a * y) / b ) ||
        ( a * y == b * z && to_mathint(f) == (b * x) / a ) || 
        ( b * y == a * z && to_mathint(f) == (a * x) / b );

// A restriction on the value of f = x * y / z
// The division quotient between x (or y) and z is an integer q or 1/q.
// Important : do not set q=0
definition constQuotient(uint256 x, uint256 y, uint256 z,
 uint256 q, uint256 f) 

        returns bool = 
        ( to_mathint(x) == q * z && to_mathint(f) == q * y ) || 
        ( q * x == to_mathint(z) && to_mathint(f)== y / q ) ||
        ( to_mathint(y) == q * z && to_mathint(f) == q * x ) || 
        ( q * y == to_mathint(z) && to_mathint(f) == x / q );


function mulDivDownAbstract(uint256 x, uint256 y, uint256 z) returns uint256 {
    uint256 f;
    require z !=0;
    require noOverFlowMul(x, y);
    require f * z <= x * y;
    require f * z + z > x * y;
    return f; 
}

/// mulDiv summary that assumes several possibilites for the quotient x/z or y/z.
/// Quotients are only integers or their reciprocals i.e. n or 1/n.
function discreteQuotientMulDiv(uint256 x, uint256 y, uint256 z) returns uint256 
{
    uint256 f;
    require z != 0 && noOverFlowMul(x, y);
    // Discrete quotients:
    require( 
        ((x ==0 || y ==0) && f == 0) || // 0
        (x == z && f == y) || // Division quotient is 1.
        (y == z && f == x) || // Division quotient is 1.
        constQuotient(x, y, z, 2, f) || // Division quotient is 1/2 or 2
        constQuotient(x, y, z, 5, f) || // Division quotient is 1/5 or 5
        constQuotient(x, y, z, 100, f) // Division quotient is 1/100 or 100
        );
    return f;
}

function discreteRatioMulDiv(uint256 x, uint256 y, uint256 z) returns uint256 
{
    uint256 f;
    require z != 0 && noOverFlowMul(x, y);
    // Discrete ratios:
    require( 
        ((x ==0 || y ==0) && f == 0) ||
        (x == z && f == y) ||
        (y == z && f == x) ||
        constRatio(x, y, z, 2, 1, f) || // f = 2*x or f = x/2 (same for y)
        constRatio(x, y, z, 5, 1, f) || // f = 5*x or f = x/5 (same for y)
        constRatio(x, y, z, 2, 3, f) || // f = 2*x/3 or f = 3*x/2 (same for y)
        constRatio(x, y, z, 2, 7, f)    // f = 2*x/7 or f = 7*x/2 (same for y)
        );
    return f;
}

function noOverFlowMul(uint256 x, uint256 y) returns bool
{
    return x * y <= max_uint;
}

function safeAdd(uint256 x, uint256 y) returns uint256
{
    return require_uint256(x + y);
}

// Check the deposit-redeem procedure for our summaries.
// Glossary:
/*  
    x - assets being deposited
    y - shares supply before deposit
    z - assets staked before deposit
    f - shares minted for deposit
    z1 - assets staked after deposit (=z+x)
    y1 - shares supply afte deposit (=y+f)
    oneShare - one share value after deposit in assets
    g - assets redeemed after calling redeem
 */

// Verified
rule checkMulDivAbstract(uint256 x, uint256 y, uint256 z) {
    uint256 f = mulDivDownAbstract(x, y, z);
    uint256 y1 = safeAdd(y, f);
    uint256 z1 = safeAdd(z, x);
    uint256 oneShare = mulDivDownAbstract(1, z1, y1);
    uint256 g = mulDivDownAbstract(f, z1, y1);
    
    // Shares and redeemed assets are non-zero.
    require g !=0 && f !=0;

    // User doesn't gain
    assert g <= x;

    // User loss is bounded by one share value.
    assert g >= x - oneShare - 1;
    //assert g >= x - oneShare ; // False
}

// Verified
rule checkSimpleMulDiv(uint256 x, uint256 y, uint256 z) {
    uint256 f = discreteQuotientMulDiv(x, y, z);
    uint256 y1 = safeAdd(y, f);
    uint256 z1 = safeAdd(z, x);
    uint256 oneShare = discreteQuotientMulDiv(1, z1, y1);
    uint256 g = discreteQuotientMulDiv(f, z1, y1);
    
    // Shares and redeemed assets are non-zero.
    require g !=0 && f !=0;

    // User doesn't gain
    assert g <= x;

    // User loss is bounded by one share value.
    assert g >= x - oneShare - 1;
    //assert g >= x - oneShare ; // False
}