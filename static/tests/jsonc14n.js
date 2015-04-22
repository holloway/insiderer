window.JSONc14n = {
    stringify: function(obj){
        var json_string,
            keys,
            key,
            i;

        switch(this.get_type(obj)){
            case "[object Array]":
                json_string = "[";
                for(i = 0; i < obj.length; i++){
                    json_string += this.stringify(obj[i]);
                    if(i < obj.length - 1) json_string += ",";
                }
                json_string += "]";
                break;
            case "[object Object]":
                json_string = "{";
                keys = Object.keys(obj);
                keys.sort();
                for(i = 0; i < keys.length; i++){
                    json_string += '"' + keys[i] + '":' + this.stringify(obj[keys[i]]);
                    if(i < keys.length - 1) json_string += ",";
                }
                json_string += "}";
                break;
            case "[object Number]":
                json_string = obj.toString();
                break;
            default:
                json_string = '"' + obj.toString().replace(/["\\]/g,
                    function(_this){
                        return function(character){
                            return _this.escape_character.apply(_this, [character]);
                        };
                    }(this)
                ) + '"';
        }
        return json_string;
    },
    get_type: function(thing){
        if(thing===null) return "[object Null]";
        return Object.prototype.toString.call(thing);
    },
    escape_character: function(character){
        return this.escape_characters[character];
    },
    escape_characters: {
        '"': '\\"',
        '\\': '\\\\'
    }
};


Object.equals = function( x, y ) {
  if ( x === y ) return true;
    // if both x and y are null or undefined and exactly the same

  if ( ! ( x instanceof Object ) || ! ( y instanceof Object ) ) return false;
    // if they are not strictly equal, they both need to be Objects

  if ( x.constructor !== y.constructor ) return false;
    // they must have the exact same prototype chain, the closest we can do is
    // test there constructor.

  for ( var p in x ) {
    if ( ! x.hasOwnProperty( p ) ) continue;
      // other properties were tested using x.constructor === y.constructor

    if ( ! y.hasOwnProperty( p ) ) return false;
      // allows to compare x[ p ] and y[ p ] when set to undefined

    if ( x[ p ] === y[ p ] ) continue;
      // if they have the same strict value or identity then they are equal

    if ( typeof( x[ p ] ) !== "object" ) return false;
      // Numbers, Strings, Functions, Booleans must be strictly equal

    if ( ! Object.equals( x[ p ],  y[ p ] ) ) return false;
      // Objects and Arrays must be tested recursively
  }

  for ( p in y ) {
    if ( y.hasOwnProperty( p ) && ! x.hasOwnProperty( p ) ) return false;
      // allows x[ p ] to be set to undefined
  }
  return true;
}
