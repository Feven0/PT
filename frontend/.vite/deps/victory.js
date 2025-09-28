import {
  InternMap,
  Symbol as Symbol2,
  appearance_default,
  arc_default,
  areaRadial_default,
  area_default,
  ascending,
  ascending_default,
  asterisk_default,
  basisClosed_default,
  basisOpen_default,
  basis_default,
  bin,
  bisect_default,
  bisector,
  bumpX,
  bumpY,
  bundle_default,
  cardinalClosed_default,
  cardinalOpen_default,
  cardinal_default,
  catmullRomClosed_default,
  catmullRomOpen_default,
  catmullRom_default,
  circle_default,
  cross_default,
  descending_default,
  diamond2_default,
  diamond_default,
  diverging_default,
  expand_default,
  extent,
  format,
  formatPrefix,
  formatSpecifier,
  insideOut_default,
  lineRadial_default,
  line_default,
  linearClosed_default,
  linear_default,
  link,
  linkHorizontal,
  linkRadial,
  linkVertical,
  max,
  min,
  monotoneX,
  monotoneY,
  natural_default,
  none_default,
  none_default2,
  now,
  number_default,
  pie_default,
  piecewise,
  plus_default,
  pointRadial_default,
  precisionFixed_default,
  precisionPrefix_default,
  precisionRound_default,
  quantile,
  quantileSorted,
  range,
  reverse_default,
  round_default,
  silhouette_default,
  square2_default,
  square_default,
  stack_default,
  star_default,
  stepAfter,
  stepBefore,
  step_default,
  symbolsFill,
  symbolsStroke,
  tickIncrement,
  tickStep,
  ticks,
  timer,
  times_default,
  triangle2_default,
  triangle_default,
  value_default,
  wiggle_default,
  wye_default
} from "./chunk-Y64MITSN.js";
import {
  require_react
} from "./chunk-7JZAKNLV.js";
import {
  __commonJS,
  __export,
  __publicField,
  __toESM
} from "./chunk-2TUXWMP5.js";

// node_modules/lodash/_arrayMap.js
var require_arrayMap = __commonJS({
  "node_modules/lodash/_arrayMap.js"(exports, module) {
    function arrayMap(array, iteratee) {
      var index = -1, length = array == null ? 0 : array.length, result = Array(length);
      while (++index < length) {
        result[index] = iteratee(array[index], index, array);
      }
      return result;
    }
    module.exports = arrayMap;
  }
});

// node_modules/lodash/isArray.js
var require_isArray = __commonJS({
  "node_modules/lodash/isArray.js"(exports, module) {
    var isArray = Array.isArray;
    module.exports = isArray;
  }
});

// node_modules/lodash/_freeGlobal.js
var require_freeGlobal = __commonJS({
  "node_modules/lodash/_freeGlobal.js"(exports, module) {
    var freeGlobal = typeof global == "object" && global && global.Object === Object && global;
    module.exports = freeGlobal;
  }
});

// node_modules/lodash/_root.js
var require_root = __commonJS({
  "node_modules/lodash/_root.js"(exports, module) {
    var freeGlobal = require_freeGlobal();
    var freeSelf = typeof self == "object" && self && self.Object === Object && self;
    var root = freeGlobal || freeSelf || Function("return this")();
    module.exports = root;
  }
});

// node_modules/lodash/_Symbol.js
var require_Symbol = __commonJS({
  "node_modules/lodash/_Symbol.js"(exports, module) {
    var root = require_root();
    var Symbol3 = root.Symbol;
    module.exports = Symbol3;
  }
});

// node_modules/lodash/_getRawTag.js
var require_getRawTag = __commonJS({
  "node_modules/lodash/_getRawTag.js"(exports, module) {
    var Symbol3 = require_Symbol();
    var objectProto = Object.prototype;
    var hasOwnProperty = objectProto.hasOwnProperty;
    var nativeObjectToString = objectProto.toString;
    var symToStringTag = Symbol3 ? Symbol3.toStringTag : void 0;
    function getRawTag(value) {
      var isOwn = hasOwnProperty.call(value, symToStringTag), tag = value[symToStringTag];
      try {
        value[symToStringTag] = void 0;
        var unmasked = true;
      } catch (e) {
      }
      var result = nativeObjectToString.call(value);
      if (unmasked) {
        if (isOwn) {
          value[symToStringTag] = tag;
        } else {
          delete value[symToStringTag];
        }
      }
      return result;
    }
    module.exports = getRawTag;
  }
});

// node_modules/lodash/_objectToString.js
var require_objectToString = __commonJS({
  "node_modules/lodash/_objectToString.js"(exports, module) {
    var objectProto = Object.prototype;
    var nativeObjectToString = objectProto.toString;
    function objectToString(value) {
      return nativeObjectToString.call(value);
    }
    module.exports = objectToString;
  }
});

// node_modules/lodash/_baseGetTag.js
var require_baseGetTag = __commonJS({
  "node_modules/lodash/_baseGetTag.js"(exports, module) {
    var Symbol3 = require_Symbol();
    var getRawTag = require_getRawTag();
    var objectToString = require_objectToString();
    var nullTag = "[object Null]";
    var undefinedTag = "[object Undefined]";
    var symToStringTag = Symbol3 ? Symbol3.toStringTag : void 0;
    function baseGetTag(value) {
      if (value == null) {
        return value === void 0 ? undefinedTag : nullTag;
      }
      return symToStringTag && symToStringTag in Object(value) ? getRawTag(value) : objectToString(value);
    }
    module.exports = baseGetTag;
  }
});

// node_modules/lodash/isObjectLike.js
var require_isObjectLike = __commonJS({
  "node_modules/lodash/isObjectLike.js"(exports, module) {
    function isObjectLike(value) {
      return value != null && typeof value == "object";
    }
    module.exports = isObjectLike;
  }
});

// node_modules/lodash/isSymbol.js
var require_isSymbol = __commonJS({
  "node_modules/lodash/isSymbol.js"(exports, module) {
    var baseGetTag = require_baseGetTag();
    var isObjectLike = require_isObjectLike();
    var symbolTag = "[object Symbol]";
    function isSymbol(value) {
      return typeof value == "symbol" || isObjectLike(value) && baseGetTag(value) == symbolTag;
    }
    module.exports = isSymbol;
  }
});

// node_modules/lodash/_isKey.js
var require_isKey = __commonJS({
  "node_modules/lodash/_isKey.js"(exports, module) {
    var isArray = require_isArray();
    var isSymbol = require_isSymbol();
    var reIsDeepProp = /\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/;
    var reIsPlainProp = /^\w*$/;
    function isKey(value, object) {
      if (isArray(value)) {
        return false;
      }
      var type = typeof value;
      if (type == "number" || type == "symbol" || type == "boolean" || value == null || isSymbol(value)) {
        return true;
      }
      return reIsPlainProp.test(value) || !reIsDeepProp.test(value) || object != null && value in Object(object);
    }
    module.exports = isKey;
  }
});

// node_modules/lodash/isObject.js
var require_isObject = __commonJS({
  "node_modules/lodash/isObject.js"(exports, module) {
    function isObject(value) {
      var type = typeof value;
      return value != null && (type == "object" || type == "function");
    }
    module.exports = isObject;
  }
});

// node_modules/lodash/isFunction.js
var require_isFunction = __commonJS({
  "node_modules/lodash/isFunction.js"(exports, module) {
    var baseGetTag = require_baseGetTag();
    var isObject = require_isObject();
    var asyncTag = "[object AsyncFunction]";
    var funcTag = "[object Function]";
    var genTag = "[object GeneratorFunction]";
    var proxyTag = "[object Proxy]";
    function isFunction2(value) {
      if (!isObject(value)) {
        return false;
      }
      var tag = baseGetTag(value);
      return tag == funcTag || tag == genTag || tag == asyncTag || tag == proxyTag;
    }
    module.exports = isFunction2;
  }
});

// node_modules/lodash/_coreJsData.js
var require_coreJsData = __commonJS({
  "node_modules/lodash/_coreJsData.js"(exports, module) {
    var root = require_root();
    var coreJsData = root["__core-js_shared__"];
    module.exports = coreJsData;
  }
});

// node_modules/lodash/_isMasked.js
var require_isMasked = __commonJS({
  "node_modules/lodash/_isMasked.js"(exports, module) {
    var coreJsData = require_coreJsData();
    var maskSrcKey = function() {
      var uid = /[^.]+$/.exec(coreJsData && coreJsData.keys && coreJsData.keys.IE_PROTO || "");
      return uid ? "Symbol(src)_1." + uid : "";
    }();
    function isMasked(func) {
      return !!maskSrcKey && maskSrcKey in func;
    }
    module.exports = isMasked;
  }
});

// node_modules/lodash/_toSource.js
var require_toSource = __commonJS({
  "node_modules/lodash/_toSource.js"(exports, module) {
    var funcProto = Function.prototype;
    var funcToString = funcProto.toString;
    function toSource(func) {
      if (func != null) {
        try {
          return funcToString.call(func);
        } catch (e) {
        }
        try {
          return func + "";
        } catch (e) {
        }
      }
      return "";
    }
    module.exports = toSource;
  }
});

// node_modules/lodash/_baseIsNative.js
var require_baseIsNative = __commonJS({
  "node_modules/lodash/_baseIsNative.js"(exports, module) {
    var isFunction2 = require_isFunction();
    var isMasked = require_isMasked();
    var isObject = require_isObject();
    var toSource = require_toSource();
    var reRegExpChar = /[\\^$.*+?()[\]{}|]/g;
    var reIsHostCtor = /^\[object .+?Constructor\]$/;
    var funcProto = Function.prototype;
    var objectProto = Object.prototype;
    var funcToString = funcProto.toString;
    var hasOwnProperty = objectProto.hasOwnProperty;
    var reIsNative = RegExp(
      "^" + funcToString.call(hasOwnProperty).replace(reRegExpChar, "\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g, "$1.*?") + "$"
    );
    function baseIsNative(value) {
      if (!isObject(value) || isMasked(value)) {
        return false;
      }
      var pattern = isFunction2(value) ? reIsNative : reIsHostCtor;
      return pattern.test(toSource(value));
    }
    module.exports = baseIsNative;
  }
});

// node_modules/lodash/_getValue.js
var require_getValue = __commonJS({
  "node_modules/lodash/_getValue.js"(exports, module) {
    function getValue(object, key) {
      return object == null ? void 0 : object[key];
    }
    module.exports = getValue;
  }
});

// node_modules/lodash/_getNative.js
var require_getNative = __commonJS({
  "node_modules/lodash/_getNative.js"(exports, module) {
    var baseIsNative = require_baseIsNative();
    var getValue = require_getValue();
    function getNative(object, key) {
      var value = getValue(object, key);
      return baseIsNative(value) ? value : void 0;
    }
    module.exports = getNative;
  }
});

// node_modules/lodash/_nativeCreate.js
var require_nativeCreate = __commonJS({
  "node_modules/lodash/_nativeCreate.js"(exports, module) {
    var getNative = require_getNative();
    var nativeCreate = getNative(Object, "create");
    module.exports = nativeCreate;
  }
});

// node_modules/lodash/_hashClear.js
var require_hashClear = __commonJS({
  "node_modules/lodash/_hashClear.js"(exports, module) {
    var nativeCreate = require_nativeCreate();
    function hashClear() {
      this.__data__ = nativeCreate ? nativeCreate(null) : {};
      this.size = 0;
    }
    module.exports = hashClear;
  }
});

// node_modules/lodash/_hashDelete.js
var require_hashDelete = __commonJS({
  "node_modules/lodash/_hashDelete.js"(exports, module) {
    function hashDelete(key) {
      var result = this.has(key) && delete this.__data__[key];
      this.size -= result ? 1 : 0;
      return result;
    }
    module.exports = hashDelete;
  }
});

// node_modules/lodash/_hashGet.js
var require_hashGet = __commonJS({
  "node_modules/lodash/_hashGet.js"(exports, module) {
    var nativeCreate = require_nativeCreate();
    var HASH_UNDEFINED = "__lodash_hash_undefined__";
    var objectProto = Object.prototype;
    var hasOwnProperty = objectProto.hasOwnProperty;
    function hashGet(key) {
      var data = this.__data__;
      if (nativeCreate) {
        var result = data[key];
        return result === HASH_UNDEFINED ? void 0 : result;
      }
      return hasOwnProperty.call(data, key) ? data[key] : void 0;
    }
    module.exports = hashGet;
  }
});

// node_modules/lodash/_hashHas.js
var require_hashHas = __commonJS({
  "node_modules/lodash/_hashHas.js"(exports, module) {
    var nativeCreate = require_nativeCreate();
    var objectProto = Object.prototype;
    var hasOwnProperty = objectProto.hasOwnProperty;
    function hashHas(key) {
      var data = this.__data__;
      return nativeCreate ? data[key] !== void 0 : hasOwnProperty.call(data, key);
    }
    module.exports = hashHas;
  }
});

// node_modules/lodash/_hashSet.js
var require_hashSet = __commonJS({
  "node_modules/lodash/_hashSet.js"(exports, module) {
    var nativeCreate = require_nativeCreate();
    var HASH_UNDEFINED = "__lodash_hash_undefined__";
    function hashSet(key, value) {
      var data = this.__data__;
      this.size += this.has(key) ? 0 : 1;
      data[key] = nativeCreate && value === void 0 ? HASH_UNDEFINED : value;
      return this;
    }
    module.exports = hashSet;
  }
});

// node_modules/lodash/_Hash.js
var require_Hash = __commonJS({
  "node_modules/lodash/_Hash.js"(exports, module) {
    var hashClear = require_hashClear();
    var hashDelete = require_hashDelete();
    var hashGet = require_hashGet();
    var hashHas = require_hashHas();
    var hashSet = require_hashSet();
    function Hash(entries) {
      var index = -1, length = entries == null ? 0 : entries.length;
      this.clear();
      while (++index < length) {
        var entry = entries[index];
        this.set(entry[0], entry[1]);
      }
    }
    Hash.prototype.clear = hashClear;
    Hash.prototype["delete"] = hashDelete;
    Hash.prototype.get = hashGet;
    Hash.prototype.has = hashHas;
    Hash.prototype.set = hashSet;
    module.exports = Hash;
  }
});

// node_modules/lodash/_listCacheClear.js
var require_listCacheClear = __commonJS({
  "node_modules/lodash/_listCacheClear.js"(exports, module) {
    function listCacheClear() {
      this.__data__ = [];
      this.size = 0;
    }
    module.exports = listCacheClear;
  }
});

// node_modules/lodash/eq.js
var require_eq = __commonJS({
  "node_modules/lodash/eq.js"(exports, module) {
    function eq(value, other) {
      return value === other || value !== value && other !== other;
    }
    module.exports = eq;
  }
});

// node_modules/lodash/_assocIndexOf.js
var require_assocIndexOf = __commonJS({
  "node_modules/lodash/_assocIndexOf.js"(exports, module) {
    var eq = require_eq();
    function assocIndexOf(array, key) {
      var length = array.length;
      while (length--) {
        if (eq(array[length][0], key)) {
          return length;
        }
      }
      return -1;
    }
    module.exports = assocIndexOf;
  }
});

// node_modules/lodash/_listCacheDelete.js
var require_listCacheDelete = __commonJS({
  "node_modules/lodash/_listCacheDelete.js"(exports, module) {
    var assocIndexOf = require_assocIndexOf();
    var arrayProto = Array.prototype;
    var splice = arrayProto.splice;
    function listCacheDelete(key) {
      var data = this.__data__, index = assocIndexOf(data, key);
      if (index < 0) {
        return false;
      }
      var lastIndex = data.length - 1;
      if (index == lastIndex) {
        data.pop();
      } else {
        splice.call(data, index, 1);
      }
      --this.size;
      return true;
    }
    module.exports = listCacheDelete;
  }
});

// node_modules/lodash/_listCacheGet.js
var require_listCacheGet = __commonJS({
  "node_modules/lodash/_listCacheGet.js"(exports, module) {
    var assocIndexOf = require_assocIndexOf();
    function listCacheGet(key) {
      var data = this.__data__, index = assocIndexOf(data, key);
      return index < 0 ? void 0 : data[index][1];
    }
    module.exports = listCacheGet;
  }
});

// node_modules/lodash/_listCacheHas.js
var require_listCacheHas = __commonJS({
  "node_modules/lodash/_listCacheHas.js"(exports, module) {
    var assocIndexOf = require_assocIndexOf();
    function listCacheHas(key) {
      return assocIndexOf(this.__data__, key) > -1;
    }
    module.exports = listCacheHas;
  }
});

// node_modules/lodash/_listCacheSet.js
var require_listCacheSet = __commonJS({
  "node_modules/lodash/_listCacheSet.js"(exports, module) {
    var assocIndexOf = require_assocIndexOf();
    function listCacheSet(key, value) {
      var data = this.__data__, index = assocIndexOf(data, key);
      if (index < 0) {
        ++this.size;
        data.push([key, value]);
      } else {
        data[index][1] = value;
      }
      return this;
    }
    module.exports = listCacheSet;
  }
});

// node_modules/lodash/_ListCache.js
var require_ListCache = __commonJS({
  "node_modules/lodash/_ListCache.js"(exports, module) {
    var listCacheClear = require_listCacheClear();
    var listCacheDelete = require_listCacheDelete();
    var listCacheGet = require_listCacheGet();
    var listCacheHas = require_listCacheHas();
    var listCacheSet = require_listCacheSet();
    function ListCache(entries) {
      var index = -1, length = entries == null ? 0 : entries.length;
      this.clear();
      while (++index < length) {
        var entry = entries[index];
        this.set(entry[0], entry[1]);
      }
    }
    ListCache.prototype.clear = listCacheClear;
    ListCache.prototype["delete"] = listCacheDelete;
    ListCache.prototype.get = listCacheGet;
    ListCache.prototype.has = listCacheHas;
    ListCache.prototype.set = listCacheSet;
    module.exports = ListCache;
  }
});

// node_modules/lodash/_Map.js
var require_Map = __commonJS({
  "node_modules/lodash/_Map.js"(exports, module) {
    var getNative = require_getNative();
    var root = require_root();
    var Map2 = getNative(root, "Map");
    module.exports = Map2;
  }
});

// node_modules/lodash/_mapCacheClear.js
var require_mapCacheClear = __commonJS({
  "node_modules/lodash/_mapCacheClear.js"(exports, module) {
    var Hash = require_Hash();
    var ListCache = require_ListCache();
    var Map2 = require_Map();
    function mapCacheClear() {
      this.size = 0;
      this.__data__ = {
        "hash": new Hash(),
        "map": new (Map2 || ListCache)(),
        "string": new Hash()
      };
    }
    module.exports = mapCacheClear;
  }
});

// node_modules/lodash/_isKeyable.js
var require_isKeyable = __commonJS({
  "node_modules/lodash/_isKeyable.js"(exports, module) {
    function isKeyable(value) {
      var type = typeof value;
      return type == "string" || type == "number" || type == "symbol" || type == "boolean" ? value !== "__proto__" : value === null;
    }
    module.exports = isKeyable;
  }
});

// node_modules/lodash/_getMapData.js
var require_getMapData = __commonJS({
  "node_modules/lodash/_getMapData.js"(exports, module) {
    var isKeyable = require_isKeyable();
    function getMapData(map, key) {
      var data = map.__data__;
      return isKeyable(key) ? data[typeof key == "string" ? "string" : "hash"] : data.map;
    }
    module.exports = getMapData;
  }
});

// node_modules/lodash/_mapCacheDelete.js
var require_mapCacheDelete = __commonJS({
  "node_modules/lodash/_mapCacheDelete.js"(exports, module) {
    var getMapData = require_getMapData();
    function mapCacheDelete(key) {
      var result = getMapData(this, key)["delete"](key);
      this.size -= result ? 1 : 0;
      return result;
    }
    module.exports = mapCacheDelete;
  }
});

// node_modules/lodash/_mapCacheGet.js
var require_mapCacheGet = __commonJS({
  "node_modules/lodash/_mapCacheGet.js"(exports, module) {
    var getMapData = require_getMapData();
    function mapCacheGet(key) {
      return getMapData(this, key).get(key);
    }
    module.exports = mapCacheGet;
  }
});

// node_modules/lodash/_mapCacheHas.js
var require_mapCacheHas = __commonJS({
  "node_modules/lodash/_mapCacheHas.js"(exports, module) {
    var getMapData = require_getMapData();
    function mapCacheHas(key) {
      return getMapData(this, key).has(key);
    }
    module.exports = mapCacheHas;
  }
});

// node_modules/lodash/_mapCacheSet.js
var require_mapCacheSet = __commonJS({
  "node_modules/lodash/_mapCacheSet.js"(exports, module) {
    var getMapData = require_getMapData();
    function mapCacheSet(key, value) {
      var data = getMapData(this, key), size = data.size;
      data.set(key, value);
      this.size += data.size == size ? 0 : 1;
      return this;
    }
    module.exports = mapCacheSet;
  }
});

// node_modules/lodash/_MapCache.js
var require_MapCache = __commonJS({
  "node_modules/lodash/_MapCache.js"(exports, module) {
    var mapCacheClear = require_mapCacheClear();
    var mapCacheDelete = require_mapCacheDelete();
    var mapCacheGet = require_mapCacheGet();
    var mapCacheHas = require_mapCacheHas();
    var mapCacheSet = require_mapCacheSet();
    function MapCache(entries) {
      var index = -1, length = entries == null ? 0 : entries.length;
      this.clear();
      while (++index < length) {
        var entry = entries[index];
        this.set(entry[0], entry[1]);
      }
    }
    MapCache.prototype.clear = mapCacheClear;
    MapCache.prototype["delete"] = mapCacheDelete;
    MapCache.prototype.get = mapCacheGet;
    MapCache.prototype.has = mapCacheHas;
    MapCache.prototype.set = mapCacheSet;
    module.exports = MapCache;
  }
});

// node_modules/lodash/memoize.js
var require_memoize = __commonJS({
  "node_modules/lodash/memoize.js"(exports, module) {
    var MapCache = require_MapCache();
    var FUNC_ERROR_TEXT = "Expected a function";
    function memoize(func, resolver) {
      if (typeof func != "function" || resolver != null && typeof resolver != "function") {
        throw new TypeError(FUNC_ERROR_TEXT);
      }
      var memoized = function() {
        var args = arguments, key = resolver ? resolver.apply(this, args) : args[0], cache = memoized.cache;
        if (cache.has(key)) {
          return cache.get(key);
        }
        var result = func.apply(this, args);
        memoized.cache = cache.set(key, result) || cache;
        return result;
      };
      memoized.cache = new (memoize.Cache || MapCache)();
      return memoized;
    }
    memoize.Cache = MapCache;
    module.exports = memoize;
  }
});

// node_modules/lodash/_memoizeCapped.js
var require_memoizeCapped = __commonJS({
  "node_modules/lodash/_memoizeCapped.js"(exports, module) {
    var memoize = require_memoize();
    var MAX_MEMOIZE_SIZE = 500;
    function memoizeCapped(func) {
      var result = memoize(func, function(key) {
        if (cache.size === MAX_MEMOIZE_SIZE) {
          cache.clear();
        }
        return key;
      });
      var cache = result.cache;
      return result;
    }
    module.exports = memoizeCapped;
  }
});

// node_modules/lodash/_stringToPath.js
var require_stringToPath = __commonJS({
  "node_modules/lodash/_stringToPath.js"(exports, module) {
    var memoizeCapped = require_memoizeCapped();
    var rePropName = /[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g;
    var reEscapeChar = /\\(\\)?/g;
    var stringToPath = memoizeCapped(function(string) {
      var result = [];
      if (string.charCodeAt(0) === 46) {
        result.push("");
      }
      string.replace(rePropName, function(match, number3, quote, subString) {
        result.push(quote ? subString.replace(reEscapeChar, "$1") : number3 || match);
      });
      return result;
    });
    module.exports = stringToPath;
  }
});

// node_modules/lodash/_baseToString.js
var require_baseToString = __commonJS({
  "node_modules/lodash/_baseToString.js"(exports, module) {
    var Symbol3 = require_Symbol();
    var arrayMap = require_arrayMap();
    var isArray = require_isArray();
    var isSymbol = require_isSymbol();
    var INFINITY = 1 / 0;
    var symbolProto = Symbol3 ? Symbol3.prototype : void 0;
    var symbolToString = symbolProto ? symbolProto.toString : void 0;
    function baseToString(value) {
      if (typeof value == "string") {
        return value;
      }
      if (isArray(value)) {
        return arrayMap(value, baseToString) + "";
      }
      if (isSymbol(value)) {
        return symbolToString ? symbolToString.call(value) : "";
      }
      var result = value + "";
      return result == "0" && 1 / value == -INFINITY ? "-0" : result;
    }
    module.exports = baseToString;
  }
});

// node_modules/lodash/toString.js
var require_toString = __commonJS({
  "node_modules/lodash/toString.js"(exports, module) {
    var baseToString = require_baseToString();
    function toString(value) {
      return value == null ? "" : baseToString(value);
    }
    module.exports = toString;
  }
});

// node_modules/lodash/_castPath.js
var require_castPath = __commonJS({
  "node_modules/lodash/_castPath.js"(exports, module) {
    var isArray = require_isArray();
    var isKey = require_isKey();
    var stringToPath = require_stringToPath();
    var toString = require_toString();
    function castPath(value, object) {
      if (isArray(value)) {
        return value;
      }
      return isKey(value, object) ? [value] : stringToPath(toString(value));
    }
    module.exports = castPath;
  }
});

// node_modules/lodash/_toKey.js
var require_toKey = __commonJS({
  "node_modules/lodash/_toKey.js"(exports, module) {
    var isSymbol = require_isSymbol();
    var INFINITY = 1 / 0;
    function toKey(value) {
      if (typeof value == "string" || isSymbol(value)) {
        return value;
      }
      var result = value + "";
      return result == "0" && 1 / value == -INFINITY ? "-0" : result;
    }
    module.exports = toKey;
  }
});

// node_modules/lodash/_baseGet.js
var require_baseGet = __commonJS({
  "node_modules/lodash/_baseGet.js"(exports, module) {
    var castPath = require_castPath();
    var toKey = require_toKey();
    function baseGet(object, path) {
      path = castPath(path, object);
      var index = 0, length = path.length;
      while (object != null && index < length) {
        object = object[toKey(path[index++])];
      }
      return index && index == length ? object : void 0;
    }
    module.exports = baseGet;
  }
});

// node_modules/lodash/_stackClear.js
var require_stackClear = __commonJS({
  "node_modules/lodash/_stackClear.js"(exports, module) {
    var ListCache = require_ListCache();
    function stackClear() {
      this.__data__ = new ListCache();
      this.size = 0;
    }
    module.exports = stackClear;
  }
});

// node_modules/lodash/_stackDelete.js
var require_stackDelete = __commonJS({
  "node_modules/lodash/_stackDelete.js"(exports, module) {
    function stackDelete(key) {
      var data = this.__data__, result = data["delete"](key);
      this.size = data.size;
      return result;
    }
    module.exports = stackDelete;
  }
});

// node_modules/lodash/_stackGet.js
var require_stackGet = __commonJS({
  "node_modules/lodash/_stackGet.js"(exports, module) {
    function stackGet(key) {
      return this.__data__.get(key);
    }
    module.exports = stackGet;
  }
});

// node_modules/lodash/_stackHas.js
var require_stackHas = __commonJS({
  "node_modules/lodash/_stackHas.js"(exports, module) {
    function stackHas(key) {
      return this.__data__.has(key);
    }
    module.exports = stackHas;
  }
});

// node_modules/lodash/_stackSet.js
var require_stackSet = __commonJS({
  "node_modules/lodash/_stackSet.js"(exports, module) {
    var ListCache = require_ListCache();
    var Map2 = require_Map();
    var MapCache = require_MapCache();
    var LARGE_ARRAY_SIZE = 200;
    function stackSet(key, value) {
      var data = this.__data__;
      if (data instanceof ListCache) {
        var pairs = data.__data__;
        if (!Map2 || pairs.length < LARGE_ARRAY_SIZE - 1) {
          pairs.push([key, value]);
          this.size = ++data.size;
          return this;
        }
        data = this.__data__ = new MapCache(pairs);
      }
      data.set(key, value);
      this.size = data.size;
      return this;
    }
    module.exports = stackSet;
  }
});

// node_modules/lodash/_Stack.js
var require_Stack = __commonJS({
  "node_modules/lodash/_Stack.js"(exports, module) {
    var ListCache = require_ListCache();
    var stackClear = require_stackClear();
    var stackDelete = require_stackDelete();
    var stackGet = require_stackGet();
    var stackHas = require_stackHas();
    var stackSet = require_stackSet();
    function Stack(entries) {
      var data = this.__data__ = new ListCache(entries);
      this.size = data.size;
    }
    Stack.prototype.clear = stackClear;
    Stack.prototype["delete"] = stackDelete;
    Stack.prototype.get = stackGet;
    Stack.prototype.has = stackHas;
    Stack.prototype.set = stackSet;
    module.exports = Stack;
  }
});

// node_modules/lodash/_setCacheAdd.js
var require_setCacheAdd = __commonJS({
  "node_modules/lodash/_setCacheAdd.js"(exports, module) {
    var HASH_UNDEFINED = "__lodash_hash_undefined__";
    function setCacheAdd(value) {
      this.__data__.set(value, HASH_UNDEFINED);
      return this;
    }
    module.exports = setCacheAdd;
  }
});

// node_modules/lodash/_setCacheHas.js
var require_setCacheHas = __commonJS({
  "node_modules/lodash/_setCacheHas.js"(exports, module) {
    function setCacheHas(value) {
      return this.__data__.has(value);
    }
    module.exports = setCacheHas;
  }
});

// node_modules/lodash/_SetCache.js
var require_SetCache = __commonJS({
  "node_modules/lodash/_SetCache.js"(exports, module) {
    var MapCache = require_MapCache();
    var setCacheAdd = require_setCacheAdd();
    var setCacheHas = require_setCacheHas();
    function SetCache(values) {
      var index = -1, length = values == null ? 0 : values.length;
      this.__data__ = new MapCache();
      while (++index < length) {
        this.add(values[index]);
      }
    }
    SetCache.prototype.add = SetCache.prototype.push = setCacheAdd;
    SetCache.prototype.has = setCacheHas;
    module.exports = SetCache;
  }
});

// node_modules/lodash/_arraySome.js
var require_arraySome = __commonJS({
  "node_modules/lodash/_arraySome.js"(exports, module) {
    function arraySome(array, predicate) {
      var index = -1, length = array == null ? 0 : array.length;
      while (++index < length) {
        if (predicate(array[index], index, array)) {
          return true;
        }
      }
      return false;
    }
    module.exports = arraySome;
  }
});

// node_modules/lodash/_cacheHas.js
var require_cacheHas = __commonJS({
  "node_modules/lodash/_cacheHas.js"(exports, module) {
    function cacheHas(cache, key) {
      return cache.has(key);
    }
    module.exports = cacheHas;
  }
});

// node_modules/lodash/_equalArrays.js
var require_equalArrays = __commonJS({
  "node_modules/lodash/_equalArrays.js"(exports, module) {
    var SetCache = require_SetCache();
    var arraySome = require_arraySome();
    var cacheHas = require_cacheHas();
    var COMPARE_PARTIAL_FLAG = 1;
    var COMPARE_UNORDERED_FLAG = 2;
    function equalArrays(array, other, bitmask, customizer, equalFunc, stack) {
      var isPartial = bitmask & COMPARE_PARTIAL_FLAG, arrLength = array.length, othLength = other.length;
      if (arrLength != othLength && !(isPartial && othLength > arrLength)) {
        return false;
      }
      var arrStacked = stack.get(array);
      var othStacked = stack.get(other);
      if (arrStacked && othStacked) {
        return arrStacked == other && othStacked == array;
      }
      var index = -1, result = true, seen = bitmask & COMPARE_UNORDERED_FLAG ? new SetCache() : void 0;
      stack.set(array, other);
      stack.set(other, array);
      while (++index < arrLength) {
        var arrValue = array[index], othValue = other[index];
        if (customizer) {
          var compared = isPartial ? customizer(othValue, arrValue, index, other, array, stack) : customizer(arrValue, othValue, index, array, other, stack);
        }
        if (compared !== void 0) {
          if (compared) {
            continue;
          }
          result = false;
          break;
        }
        if (seen) {
          if (!arraySome(other, function(othValue2, othIndex) {
            if (!cacheHas(seen, othIndex) && (arrValue === othValue2 || equalFunc(arrValue, othValue2, bitmask, customizer, stack))) {
              return seen.push(othIndex);
            }
          })) {
            result = false;
            break;
          }
        } else if (!(arrValue === othValue || equalFunc(arrValue, othValue, bitmask, customizer, stack))) {
          result = false;
          break;
        }
      }
      stack["delete"](array);
      stack["delete"](other);
      return result;
    }
    module.exports = equalArrays;
  }
});

// node_modules/lodash/_Uint8Array.js
var require_Uint8Array = __commonJS({
  "node_modules/lodash/_Uint8Array.js"(exports, module) {
    var root = require_root();
    var Uint8Array = root.Uint8Array;
    module.exports = Uint8Array;
  }
});

// node_modules/lodash/_mapToArray.js
var require_mapToArray = __commonJS({
  "node_modules/lodash/_mapToArray.js"(exports, module) {
    function mapToArray(map) {
      var index = -1, result = Array(map.size);
      map.forEach(function(value, key) {
        result[++index] = [key, value];
      });
      return result;
    }
    module.exports = mapToArray;
  }
});

// node_modules/lodash/_setToArray.js
var require_setToArray = __commonJS({
  "node_modules/lodash/_setToArray.js"(exports, module) {
    function setToArray(set) {
      var index = -1, result = Array(set.size);
      set.forEach(function(value) {
        result[++index] = value;
      });
      return result;
    }
    module.exports = setToArray;
  }
});

// node_modules/lodash/_equalByTag.js
var require_equalByTag = __commonJS({
  "node_modules/lodash/_equalByTag.js"(exports, module) {
    var Symbol3 = require_Symbol();
    var Uint8Array = require_Uint8Array();
    var eq = require_eq();
    var equalArrays = require_equalArrays();
    var mapToArray = require_mapToArray();
    var setToArray = require_setToArray();
    var COMPARE_PARTIAL_FLAG = 1;
    var COMPARE_UNORDERED_FLAG = 2;
    var boolTag = "[object Boolean]";
    var dateTag = "[object Date]";
    var errorTag = "[object Error]";
    var mapTag = "[object Map]";
    var numberTag = "[object Number]";
    var regexpTag = "[object RegExp]";
    var setTag = "[object Set]";
    var stringTag = "[object String]";
    var symbolTag = "[object Symbol]";
    var arrayBufferTag = "[object ArrayBuffer]";
    var dataViewTag = "[object DataView]";
    var symbolProto = Symbol3 ? Symbol3.prototype : void 0;
    var symbolValueOf = symbolProto ? symbolProto.valueOf : void 0;
    function equalByTag(object, other, tag, bitmask, customizer, equalFunc, stack) {
      switch (tag) {
        case dataViewTag:
          if (object.byteLength != other.byteLength || object.byteOffset != other.byteOffset) {
            return false;
          }
          object = object.buffer;
          other = other.buffer;
        case arrayBufferTag:
          if (object.byteLength != other.byteLength || !equalFunc(new Uint8Array(object), new Uint8Array(other))) {
            return false;
          }
          return true;
        case boolTag:
        case dateTag:
        case numberTag:
          return eq(+object, +other);
        case errorTag:
          return object.name == other.name && object.message == other.message;
        case regexpTag:
        case stringTag:
          return object == other + "";
        case mapTag:
          var convert = mapToArray;
        case setTag:
          var isPartial = bitmask & COMPARE_PARTIAL_FLAG;
          convert || (convert = setToArray);
          if (object.size != other.size && !isPartial) {
            return false;
          }
          var stacked = stack.get(object);
          if (stacked) {
            return stacked == other;
          }
          bitmask |= COMPARE_UNORDERED_FLAG;
          stack.set(object, other);
          var result = equalArrays(convert(object), convert(other), bitmask, customizer, equalFunc, stack);
          stack["delete"](object);
          return result;
        case symbolTag:
          if (symbolValueOf) {
            return symbolValueOf.call(object) == symbolValueOf.call(other);
          }
      }
      return false;
    }
    module.exports = equalByTag;
  }
});

// node_modules/lodash/_arrayPush.js
var require_arrayPush = __commonJS({
  "node_modules/lodash/_arrayPush.js"(exports, module) {
    function arrayPush(array, values) {
      var index = -1, length = values.length, offset = array.length;
      while (++index < length) {
        array[offset + index] = values[index];
      }
      return array;
    }
    module.exports = arrayPush;
  }
});

// node_modules/lodash/_baseGetAllKeys.js
var require_baseGetAllKeys = __commonJS({
  "node_modules/lodash/_baseGetAllKeys.js"(exports, module) {
    var arrayPush = require_arrayPush();
    var isArray = require_isArray();
    function baseGetAllKeys(object, keysFunc, symbolsFunc) {
      var result = keysFunc(object);
      return isArray(object) ? result : arrayPush(result, symbolsFunc(object));
    }
    module.exports = baseGetAllKeys;
  }
});

// node_modules/lodash/_arrayFilter.js
var require_arrayFilter = __commonJS({
  "node_modules/lodash/_arrayFilter.js"(exports, module) {
    function arrayFilter(array, predicate) {
      var index = -1, length = array == null ? 0 : array.length, resIndex = 0, result = [];
      while (++index < length) {
        var value = array[index];
        if (predicate(value, index, array)) {
          result[resIndex++] = value;
        }
      }
      return result;
    }
    module.exports = arrayFilter;
  }
});

// node_modules/lodash/stubArray.js
var require_stubArray = __commonJS({
  "node_modules/lodash/stubArray.js"(exports, module) {
    function stubArray() {
      return [];
    }
    module.exports = stubArray;
  }
});

// node_modules/lodash/_getSymbols.js
var require_getSymbols = __commonJS({
  "node_modules/lodash/_getSymbols.js"(exports, module) {
    var arrayFilter = require_arrayFilter();
    var stubArray = require_stubArray();
    var objectProto = Object.prototype;
    var propertyIsEnumerable = objectProto.propertyIsEnumerable;
    var nativeGetSymbols = Object.getOwnPropertySymbols;
    var getSymbols = !nativeGetSymbols ? stubArray : function(object) {
      if (object == null) {
        return [];
      }
      object = Object(object);
      return arrayFilter(nativeGetSymbols(object), function(symbol) {
        return propertyIsEnumerable.call(object, symbol);
      });
    };
    module.exports = getSymbols;
  }
});

// node_modules/lodash/_baseTimes.js
var require_baseTimes = __commonJS({
  "node_modules/lodash/_baseTimes.js"(exports, module) {
    function baseTimes(n, iteratee) {
      var index = -1, result = Array(n);
      while (++index < n) {
        result[index] = iteratee(index);
      }
      return result;
    }
    module.exports = baseTimes;
  }
});

// node_modules/lodash/_baseIsArguments.js
var require_baseIsArguments = __commonJS({
  "node_modules/lodash/_baseIsArguments.js"(exports, module) {
    var baseGetTag = require_baseGetTag();
    var isObjectLike = require_isObjectLike();
    var argsTag = "[object Arguments]";
    function baseIsArguments(value) {
      return isObjectLike(value) && baseGetTag(value) == argsTag;
    }
    module.exports = baseIsArguments;
  }
});

// node_modules/lodash/isArguments.js
var require_isArguments = __commonJS({
  "node_modules/lodash/isArguments.js"(exports, module) {
    var baseIsArguments = require_baseIsArguments();
    var isObjectLike = require_isObjectLike();
    var objectProto = Object.prototype;
    var hasOwnProperty = objectProto.hasOwnProperty;
    var propertyIsEnumerable = objectProto.propertyIsEnumerable;
    var isArguments = baseIsArguments(/* @__PURE__ */ function() {
      return arguments;
    }()) ? baseIsArguments : function(value) {
      return isObjectLike(value) && hasOwnProperty.call(value, "callee") && !propertyIsEnumerable.call(value, "callee");
    };
    module.exports = isArguments;
  }
});

// node_modules/lodash/stubFalse.js
var require_stubFalse = __commonJS({
  "node_modules/lodash/stubFalse.js"(exports, module) {
    function stubFalse() {
      return false;
    }
    module.exports = stubFalse;
  }
});

// node_modules/lodash/isBuffer.js
var require_isBuffer = __commonJS({
  "node_modules/lodash/isBuffer.js"(exports, module) {
    var root = require_root();
    var stubFalse = require_stubFalse();
    var freeExports = typeof exports == "object" && exports && !exports.nodeType && exports;
    var freeModule = freeExports && typeof module == "object" && module && !module.nodeType && module;
    var moduleExports = freeModule && freeModule.exports === freeExports;
    var Buffer = moduleExports ? root.Buffer : void 0;
    var nativeIsBuffer = Buffer ? Buffer.isBuffer : void 0;
    var isBuffer = nativeIsBuffer || stubFalse;
    module.exports = isBuffer;
  }
});

// node_modules/lodash/_isIndex.js
var require_isIndex = __commonJS({
  "node_modules/lodash/_isIndex.js"(exports, module) {
    var MAX_SAFE_INTEGER = 9007199254740991;
    var reIsUint = /^(?:0|[1-9]\d*)$/;
    function isIndex(value, length) {
      var type = typeof value;
      length = length == null ? MAX_SAFE_INTEGER : length;
      return !!length && (type == "number" || type != "symbol" && reIsUint.test(value)) && (value > -1 && value % 1 == 0 && value < length);
    }
    module.exports = isIndex;
  }
});

// node_modules/lodash/isLength.js
var require_isLength = __commonJS({
  "node_modules/lodash/isLength.js"(exports, module) {
    var MAX_SAFE_INTEGER = 9007199254740991;
    function isLength(value) {
      return typeof value == "number" && value > -1 && value % 1 == 0 && value <= MAX_SAFE_INTEGER;
    }
    module.exports = isLength;
  }
});

// node_modules/lodash/_baseIsTypedArray.js
var require_baseIsTypedArray = __commonJS({
  "node_modules/lodash/_baseIsTypedArray.js"(exports, module) {
    var baseGetTag = require_baseGetTag();
    var isLength = require_isLength();
    var isObjectLike = require_isObjectLike();
    var argsTag = "[object Arguments]";
    var arrayTag = "[object Array]";
    var boolTag = "[object Boolean]";
    var dateTag = "[object Date]";
    var errorTag = "[object Error]";
    var funcTag = "[object Function]";
    var mapTag = "[object Map]";
    var numberTag = "[object Number]";
    var objectTag = "[object Object]";
    var regexpTag = "[object RegExp]";
    var setTag = "[object Set]";
    var stringTag = "[object String]";
    var weakMapTag = "[object WeakMap]";
    var arrayBufferTag = "[object ArrayBuffer]";
    var dataViewTag = "[object DataView]";
    var float32Tag = "[object Float32Array]";
    var float64Tag = "[object Float64Array]";
    var int8Tag = "[object Int8Array]";
    var int16Tag = "[object Int16Array]";
    var int32Tag = "[object Int32Array]";
    var uint8Tag = "[object Uint8Array]";
    var uint8ClampedTag = "[object Uint8ClampedArray]";
    var uint16Tag = "[object Uint16Array]";
    var uint32Tag = "[object Uint32Array]";
    var typedArrayTags = {};
    typedArrayTags[float32Tag] = typedArrayTags[float64Tag] = typedArrayTags[int8Tag] = typedArrayTags[int16Tag] = typedArrayTags[int32Tag] = typedArrayTags[uint8Tag] = typedArrayTags[uint8ClampedTag] = typedArrayTags[uint16Tag] = typedArrayTags[uint32Tag] = true;
    typedArrayTags[argsTag] = typedArrayTags[arrayTag] = typedArrayTags[arrayBufferTag] = typedArrayTags[boolTag] = typedArrayTags[dataViewTag] = typedArrayTags[dateTag] = typedArrayTags[errorTag] = typedArrayTags[funcTag] = typedArrayTags[mapTag] = typedArrayTags[numberTag] = typedArrayTags[objectTag] = typedArrayTags[regexpTag] = typedArrayTags[setTag] = typedArrayTags[stringTag] = typedArrayTags[weakMapTag] = false;
    function baseIsTypedArray(value) {
      return isObjectLike(value) && isLength(value.length) && !!typedArrayTags[baseGetTag(value)];
    }
    module.exports = baseIsTypedArray;
  }
});

// node_modules/lodash/_baseUnary.js
var require_baseUnary = __commonJS({
  "node_modules/lodash/_baseUnary.js"(exports, module) {
    function baseUnary(func) {
      return function(value) {
        return func(value);
      };
    }
    module.exports = baseUnary;
  }
});

// node_modules/lodash/_nodeUtil.js
var require_nodeUtil = __commonJS({
  "node_modules/lodash/_nodeUtil.js"(exports, module) {
    var freeGlobal = require_freeGlobal();
    var freeExports = typeof exports == "object" && exports && !exports.nodeType && exports;
    var freeModule = freeExports && typeof module == "object" && module && !module.nodeType && module;
    var moduleExports = freeModule && freeModule.exports === freeExports;
    var freeProcess = moduleExports && freeGlobal.process;
    var nodeUtil = function() {
      try {
        var types = freeModule && freeModule.require && freeModule.require("util").types;
        if (types) {
          return types;
        }
        return freeProcess && freeProcess.binding && freeProcess.binding("util");
      } catch (e) {
      }
    }();
    module.exports = nodeUtil;
  }
});

// node_modules/lodash/isTypedArray.js
var require_isTypedArray = __commonJS({
  "node_modules/lodash/isTypedArray.js"(exports, module) {
    var baseIsTypedArray = require_baseIsTypedArray();
    var baseUnary = require_baseUnary();
    var nodeUtil = require_nodeUtil();
    var nodeIsTypedArray = nodeUtil && nodeUtil.isTypedArray;
    var isTypedArray = nodeIsTypedArray ? baseUnary(nodeIsTypedArray) : baseIsTypedArray;
    module.exports = isTypedArray;
  }
});

// node_modules/lodash/_arrayLikeKeys.js
var require_arrayLikeKeys = __commonJS({
  "node_modules/lodash/_arrayLikeKeys.js"(exports, module) {
    var baseTimes = require_baseTimes();
    var isArguments = require_isArguments();
    var isArray = require_isArray();
    var isBuffer = require_isBuffer();
    var isIndex = require_isIndex();
    var isTypedArray = require_isTypedArray();
    var objectProto = Object.prototype;
    var hasOwnProperty = objectProto.hasOwnProperty;
    function arrayLikeKeys(value, inherited) {
      var isArr = isArray(value), isArg = !isArr && isArguments(value), isBuff = !isArr && !isArg && isBuffer(value), isType = !isArr && !isArg && !isBuff && isTypedArray(value), skipIndexes = isArr || isArg || isBuff || isType, result = skipIndexes ? baseTimes(value.length, String) : [], length = result.length;
      for (var key in value) {
        if ((inherited || hasOwnProperty.call(value, key)) && !(skipIndexes && // Safari 9 has enumerable `arguments.length` in strict mode.
        (key == "length" || // Node.js 0.10 has enumerable non-index properties on buffers.
        isBuff && (key == "offset" || key == "parent") || // PhantomJS 2 has enumerable non-index properties on typed arrays.
        isType && (key == "buffer" || key == "byteLength" || key == "byteOffset") || // Skip index properties.
        isIndex(key, length)))) {
          result.push(key);
        }
      }
      return result;
    }
    module.exports = arrayLikeKeys;
  }
});

// node_modules/lodash/_isPrototype.js
var require_isPrototype = __commonJS({
  "node_modules/lodash/_isPrototype.js"(exports, module) {
    var objectProto = Object.prototype;
    function isPrototype(value) {
      var Ctor = value && value.constructor, proto = typeof Ctor == "function" && Ctor.prototype || objectProto;
      return value === proto;
    }
    module.exports = isPrototype;
  }
});

// node_modules/lodash/_overArg.js
var require_overArg = __commonJS({
  "node_modules/lodash/_overArg.js"(exports, module) {
    function overArg(func, transform) {
      return function(arg) {
        return func(transform(arg));
      };
    }
    module.exports = overArg;
  }
});

// node_modules/lodash/_nativeKeys.js
var require_nativeKeys = __commonJS({
  "node_modules/lodash/_nativeKeys.js"(exports, module) {
    var overArg = require_overArg();
    var nativeKeys = overArg(Object.keys, Object);
    module.exports = nativeKeys;
  }
});

// node_modules/lodash/_baseKeys.js
var require_baseKeys = __commonJS({
  "node_modules/lodash/_baseKeys.js"(exports, module) {
    var isPrototype = require_isPrototype();
    var nativeKeys = require_nativeKeys();
    var objectProto = Object.prototype;
    var hasOwnProperty = objectProto.hasOwnProperty;
    function baseKeys(object) {
      if (!isPrototype(object)) {
        return nativeKeys(object);
      }
      var result = [];
      for (var key in Object(object)) {
        if (hasOwnProperty.call(object, key) && key != "constructor") {
          result.push(key);
        }
      }
      return result;
    }
    module.exports = baseKeys;
  }
});

// node_modules/lodash/isArrayLike.js
var require_isArrayLike = __commonJS({
  "node_modules/lodash/isArrayLike.js"(exports, module) {
    var isFunction2 = require_isFunction();
    var isLength = require_isLength();
    function isArrayLike(value) {
      return value != null && isLength(value.length) && !isFunction2(value);
    }
    module.exports = isArrayLike;
  }
});

// node_modules/lodash/keys.js
var require_keys = __commonJS({
  "node_modules/lodash/keys.js"(exports, module) {
    var arrayLikeKeys = require_arrayLikeKeys();
    var baseKeys = require_baseKeys();
    var isArrayLike = require_isArrayLike();
    function keys(object) {
      return isArrayLike(object) ? arrayLikeKeys(object) : baseKeys(object);
    }
    module.exports = keys;
  }
});

// node_modules/lodash/_getAllKeys.js
var require_getAllKeys = __commonJS({
  "node_modules/lodash/_getAllKeys.js"(exports, module) {
    var baseGetAllKeys = require_baseGetAllKeys();
    var getSymbols = require_getSymbols();
    var keys = require_keys();
    function getAllKeys(object) {
      return baseGetAllKeys(object, keys, getSymbols);
    }
    module.exports = getAllKeys;
  }
});

// node_modules/lodash/_equalObjects.js
var require_equalObjects = __commonJS({
  "node_modules/lodash/_equalObjects.js"(exports, module) {
    var getAllKeys = require_getAllKeys();
    var COMPARE_PARTIAL_FLAG = 1;
    var objectProto = Object.prototype;
    var hasOwnProperty = objectProto.hasOwnProperty;
    function equalObjects(object, other, bitmask, customizer, equalFunc, stack) {
      var isPartial = bitmask & COMPARE_PARTIAL_FLAG, objProps = getAllKeys(object), objLength = objProps.length, othProps = getAllKeys(other), othLength = othProps.length;
      if (objLength != othLength && !isPartial) {
        return false;
      }
      var index = objLength;
      while (index--) {
        var key = objProps[index];
        if (!(isPartial ? key in other : hasOwnProperty.call(other, key))) {
          return false;
        }
      }
      var objStacked = stack.get(object);
      var othStacked = stack.get(other);
      if (objStacked && othStacked) {
        return objStacked == other && othStacked == object;
      }
      var result = true;
      stack.set(object, other);
      stack.set(other, object);
      var skipCtor = isPartial;
      while (++index < objLength) {
        key = objProps[index];
        var objValue = object[key], othValue = other[key];
        if (customizer) {
          var compared = isPartial ? customizer(othValue, objValue, key, other, object, stack) : customizer(objValue, othValue, key, object, other, stack);
        }
        if (!(compared === void 0 ? objValue === othValue || equalFunc(objValue, othValue, bitmask, customizer, stack) : compared)) {
          result = false;
          break;
        }
        skipCtor || (skipCtor = key == "constructor");
      }
      if (result && !skipCtor) {
        var objCtor = object.constructor, othCtor = other.constructor;
        if (objCtor != othCtor && ("constructor" in object && "constructor" in other) && !(typeof objCtor == "function" && objCtor instanceof objCtor && typeof othCtor == "function" && othCtor instanceof othCtor)) {
          result = false;
        }
      }
      stack["delete"](object);
      stack["delete"](other);
      return result;
    }
    module.exports = equalObjects;
  }
});

// node_modules/lodash/_DataView.js
var require_DataView = __commonJS({
  "node_modules/lodash/_DataView.js"(exports, module) {
    var getNative = require_getNative();
    var root = require_root();
    var DataView = getNative(root, "DataView");
    module.exports = DataView;
  }
});

// node_modules/lodash/_Promise.js
var require_Promise = __commonJS({
  "node_modules/lodash/_Promise.js"(exports, module) {
    var getNative = require_getNative();
    var root = require_root();
    var Promise2 = getNative(root, "Promise");
    module.exports = Promise2;
  }
});

// node_modules/lodash/_Set.js
var require_Set = __commonJS({
  "node_modules/lodash/_Set.js"(exports, module) {
    var getNative = require_getNative();
    var root = require_root();
    var Set2 = getNative(root, "Set");
    module.exports = Set2;
  }
});

// node_modules/lodash/_WeakMap.js
var require_WeakMap = __commonJS({
  "node_modules/lodash/_WeakMap.js"(exports, module) {
    var getNative = require_getNative();
    var root = require_root();
    var WeakMap = getNative(root, "WeakMap");
    module.exports = WeakMap;
  }
});

// node_modules/lodash/_getTag.js
var require_getTag = __commonJS({
  "node_modules/lodash/_getTag.js"(exports, module) {
    var DataView = require_DataView();
    var Map2 = require_Map();
    var Promise2 = require_Promise();
    var Set2 = require_Set();
    var WeakMap = require_WeakMap();
    var baseGetTag = require_baseGetTag();
    var toSource = require_toSource();
    var mapTag = "[object Map]";
    var objectTag = "[object Object]";
    var promiseTag = "[object Promise]";
    var setTag = "[object Set]";
    var weakMapTag = "[object WeakMap]";
    var dataViewTag = "[object DataView]";
    var dataViewCtorString = toSource(DataView);
    var mapCtorString = toSource(Map2);
    var promiseCtorString = toSource(Promise2);
    var setCtorString = toSource(Set2);
    var weakMapCtorString = toSource(WeakMap);
    var getTag = baseGetTag;
    if (DataView && getTag(new DataView(new ArrayBuffer(1))) != dataViewTag || Map2 && getTag(new Map2()) != mapTag || Promise2 && getTag(Promise2.resolve()) != promiseTag || Set2 && getTag(new Set2()) != setTag || WeakMap && getTag(new WeakMap()) != weakMapTag) {
      getTag = function(value) {
        var result = baseGetTag(value), Ctor = result == objectTag ? value.constructor : void 0, ctorString = Ctor ? toSource(Ctor) : "";
        if (ctorString) {
          switch (ctorString) {
            case dataViewCtorString:
              return dataViewTag;
            case mapCtorString:
              return mapTag;
            case promiseCtorString:
              return promiseTag;
            case setCtorString:
              return setTag;
            case weakMapCtorString:
              return weakMapTag;
          }
        }
        return result;
      };
    }
    module.exports = getTag;
  }
});

// node_modules/lodash/_baseIsEqualDeep.js
var require_baseIsEqualDeep = __commonJS({
  "node_modules/lodash/_baseIsEqualDeep.js"(exports, module) {
    var Stack = require_Stack();
    var equalArrays = require_equalArrays();
    var equalByTag = require_equalByTag();
    var equalObjects = require_equalObjects();
    var getTag = require_getTag();
    var isArray = require_isArray();
    var isBuffer = require_isBuffer();
    var isTypedArray = require_isTypedArray();
    var COMPARE_PARTIAL_FLAG = 1;
    var argsTag = "[object Arguments]";
    var arrayTag = "[object Array]";
    var objectTag = "[object Object]";
    var objectProto = Object.prototype;
    var hasOwnProperty = objectProto.hasOwnProperty;
    function baseIsEqualDeep(object, other, bitmask, customizer, equalFunc, stack) {
      var objIsArr = isArray(object), othIsArr = isArray(other), objTag = objIsArr ? arrayTag : getTag(object), othTag = othIsArr ? arrayTag : getTag(other);
      objTag = objTag == argsTag ? objectTag : objTag;
      othTag = othTag == argsTag ? objectTag : othTag;
      var objIsObj = objTag == objectTag, othIsObj = othTag == objectTag, isSameTag = objTag == othTag;
      if (isSameTag && isBuffer(object)) {
        if (!isBuffer(other)) {
          return false;
        }
        objIsArr = true;
        objIsObj = false;
      }
      if (isSameTag && !objIsObj) {
        stack || (stack = new Stack());
        return objIsArr || isTypedArray(object) ? equalArrays(object, other, bitmask, customizer, equalFunc, stack) : equalByTag(object, other, objTag, bitmask, customizer, equalFunc, stack);
      }
      if (!(bitmask & COMPARE_PARTIAL_FLAG)) {
        var objIsWrapped = objIsObj && hasOwnProperty.call(object, "__wrapped__"), othIsWrapped = othIsObj && hasOwnProperty.call(other, "__wrapped__");
        if (objIsWrapped || othIsWrapped) {
          var objUnwrapped = objIsWrapped ? object.value() : object, othUnwrapped = othIsWrapped ? other.value() : other;
          stack || (stack = new Stack());
          return equalFunc(objUnwrapped, othUnwrapped, bitmask, customizer, stack);
        }
      }
      if (!isSameTag) {
        return false;
      }
      stack || (stack = new Stack());
      return equalObjects(object, other, bitmask, customizer, equalFunc, stack);
    }
    module.exports = baseIsEqualDeep;
  }
});

// node_modules/lodash/_baseIsEqual.js
var require_baseIsEqual = __commonJS({
  "node_modules/lodash/_baseIsEqual.js"(exports, module) {
    var baseIsEqualDeep = require_baseIsEqualDeep();
    var isObjectLike = require_isObjectLike();
    function baseIsEqual(value, other, bitmask, customizer, stack) {
      if (value === other) {
        return true;
      }
      if (value == null || other == null || !isObjectLike(value) && !isObjectLike(other)) {
        return value !== value && other !== other;
      }
      return baseIsEqualDeep(value, other, bitmask, customizer, baseIsEqual, stack);
    }
    module.exports = baseIsEqual;
  }
});

// node_modules/lodash/_baseIsMatch.js
var require_baseIsMatch = __commonJS({
  "node_modules/lodash/_baseIsMatch.js"(exports, module) {
    var Stack = require_Stack();
    var baseIsEqual = require_baseIsEqual();
    var COMPARE_PARTIAL_FLAG = 1;
    var COMPARE_UNORDERED_FLAG = 2;
    function baseIsMatch(object, source, matchData, customizer) {
      var index = matchData.length, length = index, noCustomizer = !customizer;
      if (object == null) {
        return !length;
      }
      object = Object(object);
      while (index--) {
        var data = matchData[index];
        if (noCustomizer && data[2] ? data[1] !== object[data[0]] : !(data[0] in object)) {
          return false;
        }
      }
      while (++index < length) {
        data = matchData[index];
        var key = data[0], objValue = object[key], srcValue = data[1];
        if (noCustomizer && data[2]) {
          if (objValue === void 0 && !(key in object)) {
            return false;
          }
        } else {
          var stack = new Stack();
          if (customizer) {
            var result = customizer(objValue, srcValue, key, object, source, stack);
          }
          if (!(result === void 0 ? baseIsEqual(srcValue, objValue, COMPARE_PARTIAL_FLAG | COMPARE_UNORDERED_FLAG, customizer, stack) : result)) {
            return false;
          }
        }
      }
      return true;
    }
    module.exports = baseIsMatch;
  }
});

// node_modules/lodash/_isStrictComparable.js
var require_isStrictComparable = __commonJS({
  "node_modules/lodash/_isStrictComparable.js"(exports, module) {
    var isObject = require_isObject();
    function isStrictComparable(value) {
      return value === value && !isObject(value);
    }
    module.exports = isStrictComparable;
  }
});

// node_modules/lodash/_getMatchData.js
var require_getMatchData = __commonJS({
  "node_modules/lodash/_getMatchData.js"(exports, module) {
    var isStrictComparable = require_isStrictComparable();
    var keys = require_keys();
    function getMatchData(object) {
      var result = keys(object), length = result.length;
      while (length--) {
        var key = result[length], value = object[key];
        result[length] = [key, value, isStrictComparable(value)];
      }
      return result;
    }
    module.exports = getMatchData;
  }
});

// node_modules/lodash/_matchesStrictComparable.js
var require_matchesStrictComparable = __commonJS({
  "node_modules/lodash/_matchesStrictComparable.js"(exports, module) {
    function matchesStrictComparable(key, srcValue) {
      return function(object) {
        if (object == null) {
          return false;
        }
        return object[key] === srcValue && (srcValue !== void 0 || key in Object(object));
      };
    }
    module.exports = matchesStrictComparable;
  }
});

// node_modules/lodash/_baseMatches.js
var require_baseMatches = __commonJS({
  "node_modules/lodash/_baseMatches.js"(exports, module) {
    var baseIsMatch = require_baseIsMatch();
    var getMatchData = require_getMatchData();
    var matchesStrictComparable = require_matchesStrictComparable();
    function baseMatches(source) {
      var matchData = getMatchData(source);
      if (matchData.length == 1 && matchData[0][2]) {
        return matchesStrictComparable(matchData[0][0], matchData[0][1]);
      }
      return function(object) {
        return object === source || baseIsMatch(object, source, matchData);
      };
    }
    module.exports = baseMatches;
  }
});

// node_modules/lodash/get.js
var require_get = __commonJS({
  "node_modules/lodash/get.js"(exports, module) {
    var baseGet = require_baseGet();
    function get(object, path, defaultValue) {
      var result = object == null ? void 0 : baseGet(object, path);
      return result === void 0 ? defaultValue : result;
    }
    module.exports = get;
  }
});

// node_modules/lodash/_baseHasIn.js
var require_baseHasIn = __commonJS({
  "node_modules/lodash/_baseHasIn.js"(exports, module) {
    function baseHasIn(object, key) {
      return object != null && key in Object(object);
    }
    module.exports = baseHasIn;
  }
});

// node_modules/lodash/_hasPath.js
var require_hasPath = __commonJS({
  "node_modules/lodash/_hasPath.js"(exports, module) {
    var castPath = require_castPath();
    var isArguments = require_isArguments();
    var isArray = require_isArray();
    var isIndex = require_isIndex();
    var isLength = require_isLength();
    var toKey = require_toKey();
    function hasPath(object, path, hasFunc) {
      path = castPath(path, object);
      var index = -1, length = path.length, result = false;
      while (++index < length) {
        var key = toKey(path[index]);
        if (!(result = object != null && hasFunc(object, key))) {
          break;
        }
        object = object[key];
      }
      if (result || ++index != length) {
        return result;
      }
      length = object == null ? 0 : object.length;
      return !!length && isLength(length) && isIndex(key, length) && (isArray(object) || isArguments(object));
    }
    module.exports = hasPath;
  }
});

// node_modules/lodash/hasIn.js
var require_hasIn = __commonJS({
  "node_modules/lodash/hasIn.js"(exports, module) {
    var baseHasIn = require_baseHasIn();
    var hasPath = require_hasPath();
    function hasIn(object, path) {
      return object != null && hasPath(object, path, baseHasIn);
    }
    module.exports = hasIn;
  }
});

// node_modules/lodash/_baseMatchesProperty.js
var require_baseMatchesProperty = __commonJS({
  "node_modules/lodash/_baseMatchesProperty.js"(exports, module) {
    var baseIsEqual = require_baseIsEqual();
    var get = require_get();
    var hasIn = require_hasIn();
    var isKey = require_isKey();
    var isStrictComparable = require_isStrictComparable();
    var matchesStrictComparable = require_matchesStrictComparable();
    var toKey = require_toKey();
    var COMPARE_PARTIAL_FLAG = 1;
    var COMPARE_UNORDERED_FLAG = 2;
    function baseMatchesProperty(path, srcValue) {
      if (isKey(path) && isStrictComparable(srcValue)) {
        return matchesStrictComparable(toKey(path), srcValue);
      }
      return function(object) {
        var objValue = get(object, path);
        return objValue === void 0 && objValue === srcValue ? hasIn(object, path) : baseIsEqual(srcValue, objValue, COMPARE_PARTIAL_FLAG | COMPARE_UNORDERED_FLAG);
      };
    }
    module.exports = baseMatchesProperty;
  }
});

// node_modules/lodash/identity.js
var require_identity = __commonJS({
  "node_modules/lodash/identity.js"(exports, module) {
    function identity4(value) {
      return value;
    }
    module.exports = identity4;
  }
});

// node_modules/lodash/_baseProperty.js
var require_baseProperty = __commonJS({
  "node_modules/lodash/_baseProperty.js"(exports, module) {
    function baseProperty(key) {
      return function(object) {
        return object == null ? void 0 : object[key];
      };
    }
    module.exports = baseProperty;
  }
});

// node_modules/lodash/_basePropertyDeep.js
var require_basePropertyDeep = __commonJS({
  "node_modules/lodash/_basePropertyDeep.js"(exports, module) {
    var baseGet = require_baseGet();
    function basePropertyDeep(path) {
      return function(object) {
        return baseGet(object, path);
      };
    }
    module.exports = basePropertyDeep;
  }
});

// node_modules/lodash/property.js
var require_property = __commonJS({
  "node_modules/lodash/property.js"(exports, module) {
    var baseProperty = require_baseProperty();
    var basePropertyDeep = require_basePropertyDeep();
    var isKey = require_isKey();
    var toKey = require_toKey();
    function property(path) {
      return isKey(path) ? baseProperty(toKey(path)) : basePropertyDeep(path);
    }
    module.exports = property;
  }
});

// node_modules/lodash/_baseIteratee.js
var require_baseIteratee = __commonJS({
  "node_modules/lodash/_baseIteratee.js"(exports, module) {
    var baseMatches = require_baseMatches();
    var baseMatchesProperty = require_baseMatchesProperty();
    var identity4 = require_identity();
    var isArray = require_isArray();
    var property = require_property();
    function baseIteratee(value) {
      if (typeof value == "function") {
        return value;
      }
      if (value == null) {
        return identity4;
      }
      if (typeof value == "object") {
        return isArray(value) ? baseMatchesProperty(value[0], value[1]) : baseMatches(value);
      }
      return property(value);
    }
    module.exports = baseIteratee;
  }
});

// node_modules/lodash/_createBaseFor.js
var require_createBaseFor = __commonJS({
  "node_modules/lodash/_createBaseFor.js"(exports, module) {
    function createBaseFor(fromRight) {
      return function(object, iteratee, keysFunc) {
        var index = -1, iterable = Object(object), props = keysFunc(object), length = props.length;
        while (length--) {
          var key = props[fromRight ? length : ++index];
          if (iteratee(iterable[key], key, iterable) === false) {
            break;
          }
        }
        return object;
      };
    }
    module.exports = createBaseFor;
  }
});

// node_modules/lodash/_baseFor.js
var require_baseFor = __commonJS({
  "node_modules/lodash/_baseFor.js"(exports, module) {
    var createBaseFor = require_createBaseFor();
    var baseFor = createBaseFor();
    module.exports = baseFor;
  }
});

// node_modules/lodash/_baseForOwn.js
var require_baseForOwn = __commonJS({
  "node_modules/lodash/_baseForOwn.js"(exports, module) {
    var baseFor = require_baseFor();
    var keys = require_keys();
    function baseForOwn(object, iteratee) {
      return object && baseFor(object, iteratee, keys);
    }
    module.exports = baseForOwn;
  }
});

// node_modules/lodash/_createBaseEach.js
var require_createBaseEach = __commonJS({
  "node_modules/lodash/_createBaseEach.js"(exports, module) {
    var isArrayLike = require_isArrayLike();
    function createBaseEach(eachFunc, fromRight) {
      return function(collection, iteratee) {
        if (collection == null) {
          return collection;
        }
        if (!isArrayLike(collection)) {
          return eachFunc(collection, iteratee);
        }
        var length = collection.length, index = fromRight ? length : -1, iterable = Object(collection);
        while (fromRight ? index-- : ++index < length) {
          if (iteratee(iterable[index], index, iterable) === false) {
            break;
          }
        }
        return collection;
      };
    }
    module.exports = createBaseEach;
  }
});

// node_modules/lodash/_baseEach.js
var require_baseEach = __commonJS({
  "node_modules/lodash/_baseEach.js"(exports, module) {
    var baseForOwn = require_baseForOwn();
    var createBaseEach = require_createBaseEach();
    var baseEach = createBaseEach(baseForOwn);
    module.exports = baseEach;
  }
});

// node_modules/lodash/_baseMap.js
var require_baseMap = __commonJS({
  "node_modules/lodash/_baseMap.js"(exports, module) {
    var baseEach = require_baseEach();
    var isArrayLike = require_isArrayLike();
    function baseMap(collection, iteratee) {
      var index = -1, result = isArrayLike(collection) ? Array(collection.length) : [];
      baseEach(collection, function(value, key, collection2) {
        result[++index] = iteratee(value, key, collection2);
      });
      return result;
    }
    module.exports = baseMap;
  }
});

// node_modules/lodash/_baseSortBy.js
var require_baseSortBy = __commonJS({
  "node_modules/lodash/_baseSortBy.js"(exports, module) {
    function baseSortBy(array, comparer) {
      var length = array.length;
      array.sort(comparer);
      while (length--) {
        array[length] = array[length].value;
      }
      return array;
    }
    module.exports = baseSortBy;
  }
});

// node_modules/lodash/_compareAscending.js
var require_compareAscending = __commonJS({
  "node_modules/lodash/_compareAscending.js"(exports, module) {
    var isSymbol = require_isSymbol();
    function compareAscending(value, other) {
      if (value !== other) {
        var valIsDefined = value !== void 0, valIsNull = value === null, valIsReflexive = value === value, valIsSymbol = isSymbol(value);
        var othIsDefined = other !== void 0, othIsNull = other === null, othIsReflexive = other === other, othIsSymbol = isSymbol(other);
        if (!othIsNull && !othIsSymbol && !valIsSymbol && value > other || valIsSymbol && othIsDefined && othIsReflexive && !othIsNull && !othIsSymbol || valIsNull && othIsDefined && othIsReflexive || !valIsDefined && othIsReflexive || !valIsReflexive) {
          return 1;
        }
        if (!valIsNull && !valIsSymbol && !othIsSymbol && value < other || othIsSymbol && valIsDefined && valIsReflexive && !valIsNull && !valIsSymbol || othIsNull && valIsDefined && valIsReflexive || !othIsDefined && valIsReflexive || !othIsReflexive) {
          return -1;
        }
      }
      return 0;
    }
    module.exports = compareAscending;
  }
});

// node_modules/lodash/_compareMultiple.js
var require_compareMultiple = __commonJS({
  "node_modules/lodash/_compareMultiple.js"(exports, module) {
    var compareAscending = require_compareAscending();
    function compareMultiple(object, other, orders) {
      var index = -1, objCriteria = object.criteria, othCriteria = other.criteria, length = objCriteria.length, ordersLength = orders.length;
      while (++index < length) {
        var result = compareAscending(objCriteria[index], othCriteria[index]);
        if (result) {
          if (index >= ordersLength) {
            return result;
          }
          var order = orders[index];
          return result * (order == "desc" ? -1 : 1);
        }
      }
      return object.index - other.index;
    }
    module.exports = compareMultiple;
  }
});

// node_modules/lodash/_baseOrderBy.js
var require_baseOrderBy = __commonJS({
  "node_modules/lodash/_baseOrderBy.js"(exports, module) {
    var arrayMap = require_arrayMap();
    var baseGet = require_baseGet();
    var baseIteratee = require_baseIteratee();
    var baseMap = require_baseMap();
    var baseSortBy = require_baseSortBy();
    var baseUnary = require_baseUnary();
    var compareMultiple = require_compareMultiple();
    var identity4 = require_identity();
    var isArray = require_isArray();
    function baseOrderBy(collection, iteratees, orders) {
      if (iteratees.length) {
        iteratees = arrayMap(iteratees, function(iteratee) {
          if (isArray(iteratee)) {
            return function(value) {
              return baseGet(value, iteratee.length === 1 ? iteratee[0] : iteratee);
            };
          }
          return iteratee;
        });
      } else {
        iteratees = [identity4];
      }
      var index = -1;
      iteratees = arrayMap(iteratees, baseUnary(baseIteratee));
      var result = baseMap(collection, function(value, key, collection2) {
        var criteria = arrayMap(iteratees, function(iteratee) {
          return iteratee(value);
        });
        return { "criteria": criteria, "index": ++index, "value": value };
      });
      return baseSortBy(result, function(object, other) {
        return compareMultiple(object, other, orders);
      });
    }
    module.exports = baseOrderBy;
  }
});

// node_modules/lodash/orderBy.js
var require_orderBy = __commonJS({
  "node_modules/lodash/orderBy.js"(exports, module) {
    var baseOrderBy = require_baseOrderBy();
    var isArray = require_isArray();
    function orderBy(collection, iteratees, orders, guard) {
      if (collection == null) {
        return [];
      }
      if (!isArray(iteratees)) {
        iteratees = iteratees == null ? [] : [iteratees];
      }
      orders = guard ? void 0 : orders;
      if (!isArray(orders)) {
        orders = orders == null ? [] : [orders];
      }
      return baseOrderBy(collection, iteratees, orders);
    }
    module.exports = orderBy;
  }
});

// node_modules/lodash/_getPrototype.js
var require_getPrototype = __commonJS({
  "node_modules/lodash/_getPrototype.js"(exports, module) {
    var overArg = require_overArg();
    var getPrototype = overArg(Object.getPrototypeOf, Object);
    module.exports = getPrototype;
  }
});

// node_modules/lodash/isPlainObject.js
var require_isPlainObject = __commonJS({
  "node_modules/lodash/isPlainObject.js"(exports, module) {
    var baseGetTag = require_baseGetTag();
    var getPrototype = require_getPrototype();
    var isObjectLike = require_isObjectLike();
    var objectTag = "[object Object]";
    var funcProto = Function.prototype;
    var objectProto = Object.prototype;
    var funcToString = funcProto.toString;
    var hasOwnProperty = objectProto.hasOwnProperty;
    var objectCtorString = funcToString.call(Object);
    function isPlainObject(value) {
      if (!isObjectLike(value) || baseGetTag(value) != objectTag) {
        return false;
      }
      var proto = getPrototype(value);
      if (proto === null) {
        return true;
      }
      var Ctor = hasOwnProperty.call(proto, "constructor") && proto.constructor;
      return typeof Ctor == "function" && Ctor instanceof Ctor && funcToString.call(Ctor) == objectCtorString;
    }
    module.exports = isPlainObject;
  }
});

// node_modules/lodash/uniqueId.js
var require_uniqueId = __commonJS({
  "node_modules/lodash/uniqueId.js"(exports, module) {
    var toString = require_toString();
    var idCounter = 0;
    function uniqueId(prefix) {
      var id = ++idCounter;
      return toString(prefix) + id;
    }
    module.exports = uniqueId;
  }
});

// node_modules/lodash/_defineProperty.js
var require_defineProperty = __commonJS({
  "node_modules/lodash/_defineProperty.js"(exports, module) {
    var getNative = require_getNative();
    var defineProperty = function() {
      try {
        var func = getNative(Object, "defineProperty");
        func({}, "", {});
        return func;
      } catch (e) {
      }
    }();
    module.exports = defineProperty;
  }
});

// node_modules/lodash/_baseAssignValue.js
var require_baseAssignValue = __commonJS({
  "node_modules/lodash/_baseAssignValue.js"(exports, module) {
    var defineProperty = require_defineProperty();
    function baseAssignValue(object, key, value) {
      if (key == "__proto__" && defineProperty) {
        defineProperty(object, key, {
          "configurable": true,
          "enumerable": true,
          "value": value,
          "writable": true
        });
      } else {
        object[key] = value;
      }
    }
    module.exports = baseAssignValue;
  }
});

// node_modules/lodash/_assignValue.js
var require_assignValue = __commonJS({
  "node_modules/lodash/_assignValue.js"(exports, module) {
    var baseAssignValue = require_baseAssignValue();
    var eq = require_eq();
    var objectProto = Object.prototype;
    var hasOwnProperty = objectProto.hasOwnProperty;
    function assignValue(object, key, value) {
      var objValue = object[key];
      if (!(hasOwnProperty.call(object, key) && eq(objValue, value)) || value === void 0 && !(key in object)) {
        baseAssignValue(object, key, value);
      }
    }
    module.exports = assignValue;
  }
});

// node_modules/lodash/_baseSet.js
var require_baseSet = __commonJS({
  "node_modules/lodash/_baseSet.js"(exports, module) {
    var assignValue = require_assignValue();
    var castPath = require_castPath();
    var isIndex = require_isIndex();
    var isObject = require_isObject();
    var toKey = require_toKey();
    function baseSet(object, path, value, customizer) {
      if (!isObject(object)) {
        return object;
      }
      path = castPath(path, object);
      var index = -1, length = path.length, lastIndex = length - 1, nested = object;
      while (nested != null && ++index < length) {
        var key = toKey(path[index]), newValue = value;
        if (key === "__proto__" || key === "constructor" || key === "prototype") {
          return object;
        }
        if (index != lastIndex) {
          var objValue = nested[key];
          newValue = customizer ? customizer(objValue, key, nested) : void 0;
          if (newValue === void 0) {
            newValue = isObject(objValue) ? objValue : isIndex(path[index + 1]) ? [] : {};
          }
        }
        assignValue(nested, key, newValue);
        nested = nested[key];
      }
      return object;
    }
    module.exports = baseSet;
  }
});

// node_modules/lodash/_basePickBy.js
var require_basePickBy = __commonJS({
  "node_modules/lodash/_basePickBy.js"(exports, module) {
    var baseGet = require_baseGet();
    var baseSet = require_baseSet();
    var castPath = require_castPath();
    function basePickBy(object, paths, predicate) {
      var index = -1, length = paths.length, result = {};
      while (++index < length) {
        var path = paths[index], value = baseGet(object, path);
        if (predicate(value, path)) {
          baseSet(result, castPath(path, object), value);
        }
      }
      return result;
    }
    module.exports = basePickBy;
  }
});

// node_modules/lodash/_basePick.js
var require_basePick = __commonJS({
  "node_modules/lodash/_basePick.js"(exports, module) {
    var basePickBy = require_basePickBy();
    var hasIn = require_hasIn();
    function basePick(object, paths) {
      return basePickBy(object, paths, function(value, path) {
        return hasIn(object, path);
      });
    }
    module.exports = basePick;
  }
});

// node_modules/lodash/_isFlattenable.js
var require_isFlattenable = __commonJS({
  "node_modules/lodash/_isFlattenable.js"(exports, module) {
    var Symbol3 = require_Symbol();
    var isArguments = require_isArguments();
    var isArray = require_isArray();
    var spreadableSymbol = Symbol3 ? Symbol3.isConcatSpreadable : void 0;
    function isFlattenable(value) {
      return isArray(value) || isArguments(value) || !!(spreadableSymbol && value && value[spreadableSymbol]);
    }
    module.exports = isFlattenable;
  }
});

// node_modules/lodash/_baseFlatten.js
var require_baseFlatten = __commonJS({
  "node_modules/lodash/_baseFlatten.js"(exports, module) {
    var arrayPush = require_arrayPush();
    var isFlattenable = require_isFlattenable();
    function baseFlatten(array, depth, predicate, isStrict, result) {
      var index = -1, length = array.length;
      predicate || (predicate = isFlattenable);
      result || (result = []);
      while (++index < length) {
        var value = array[index];
        if (depth > 0 && predicate(value)) {
          if (depth > 1) {
            baseFlatten(value, depth - 1, predicate, isStrict, result);
          } else {
            arrayPush(result, value);
          }
        } else if (!isStrict) {
          result[result.length] = value;
        }
      }
      return result;
    }
    module.exports = baseFlatten;
  }
});

// node_modules/lodash/flatten.js
var require_flatten = __commonJS({
  "node_modules/lodash/flatten.js"(exports, module) {
    var baseFlatten = require_baseFlatten();
    function flatten(array) {
      var length = array == null ? 0 : array.length;
      return length ? baseFlatten(array, 1) : [];
    }
    module.exports = flatten;
  }
});

// node_modules/lodash/_apply.js
var require_apply = __commonJS({
  "node_modules/lodash/_apply.js"(exports, module) {
    function apply(func, thisArg, args) {
      switch (args.length) {
        case 0:
          return func.call(thisArg);
        case 1:
          return func.call(thisArg, args[0]);
        case 2:
          return func.call(thisArg, args[0], args[1]);
        case 3:
          return func.call(thisArg, args[0], args[1], args[2]);
      }
      return func.apply(thisArg, args);
    }
    module.exports = apply;
  }
});

// node_modules/lodash/_overRest.js
var require_overRest = __commonJS({
  "node_modules/lodash/_overRest.js"(exports, module) {
    var apply = require_apply();
    var nativeMax = Math.max;
    function overRest(func, start, transform) {
      start = nativeMax(start === void 0 ? func.length - 1 : start, 0);
      return function() {
        var args = arguments, index = -1, length = nativeMax(args.length - start, 0), array = Array(length);
        while (++index < length) {
          array[index] = args[start + index];
        }
        index = -1;
        var otherArgs = Array(start + 1);
        while (++index < start) {
          otherArgs[index] = args[index];
        }
        otherArgs[start] = transform(array);
        return apply(func, this, otherArgs);
      };
    }
    module.exports = overRest;
  }
});

// node_modules/lodash/constant.js
var require_constant = __commonJS({
  "node_modules/lodash/constant.js"(exports, module) {
    function constant(value) {
      return function() {
        return value;
      };
    }
    module.exports = constant;
  }
});

// node_modules/lodash/_baseSetToString.js
var require_baseSetToString = __commonJS({
  "node_modules/lodash/_baseSetToString.js"(exports, module) {
    var constant = require_constant();
    var defineProperty = require_defineProperty();
    var identity4 = require_identity();
    var baseSetToString = !defineProperty ? identity4 : function(func, string) {
      return defineProperty(func, "toString", {
        "configurable": true,
        "enumerable": false,
        "value": constant(string),
        "writable": true
      });
    };
    module.exports = baseSetToString;
  }
});

// node_modules/lodash/_shortOut.js
var require_shortOut = __commonJS({
  "node_modules/lodash/_shortOut.js"(exports, module) {
    var HOT_COUNT = 800;
    var HOT_SPAN = 16;
    var nativeNow = Date.now;
    function shortOut(func) {
      var count = 0, lastCalled = 0;
      return function() {
        var stamp = nativeNow(), remaining = HOT_SPAN - (stamp - lastCalled);
        lastCalled = stamp;
        if (remaining > 0) {
          if (++count >= HOT_COUNT) {
            return arguments[0];
          }
        } else {
          count = 0;
        }
        return func.apply(void 0, arguments);
      };
    }
    module.exports = shortOut;
  }
});

// node_modules/lodash/_setToString.js
var require_setToString = __commonJS({
  "node_modules/lodash/_setToString.js"(exports, module) {
    var baseSetToString = require_baseSetToString();
    var shortOut = require_shortOut();
    var setToString = shortOut(baseSetToString);
    module.exports = setToString;
  }
});

// node_modules/lodash/_flatRest.js
var require_flatRest = __commonJS({
  "node_modules/lodash/_flatRest.js"(exports, module) {
    var flatten = require_flatten();
    var overRest = require_overRest();
    var setToString = require_setToString();
    function flatRest(func) {
      return setToString(overRest(func, void 0, flatten), func + "");
    }
    module.exports = flatRest;
  }
});

// node_modules/lodash/pick.js
var require_pick = __commonJS({
  "node_modules/lodash/pick.js"(exports, module) {
    var basePick = require_basePick();
    var flatRest = require_flatRest();
    var pick = flatRest(function(object, paths) {
      return object == null ? {} : basePick(object, paths);
    });
    module.exports = pick;
  }
});

// node_modules/lodash/_baseRest.js
var require_baseRest = __commonJS({
  "node_modules/lodash/_baseRest.js"(exports, module) {
    var identity4 = require_identity();
    var overRest = require_overRest();
    var setToString = require_setToString();
    function baseRest(func, start) {
      return setToString(overRest(func, start, identity4), func + "");
    }
    module.exports = baseRest;
  }
});

// node_modules/lodash/_isIterateeCall.js
var require_isIterateeCall = __commonJS({
  "node_modules/lodash/_isIterateeCall.js"(exports, module) {
    var eq = require_eq();
    var isArrayLike = require_isArrayLike();
    var isIndex = require_isIndex();
    var isObject = require_isObject();
    function isIterateeCall(value, index, object) {
      if (!isObject(object)) {
        return false;
      }
      var type = typeof index;
      if (type == "number" ? isArrayLike(object) && isIndex(index, object.length) : type == "string" && index in object) {
        return eq(object[index], value);
      }
      return false;
    }
    module.exports = isIterateeCall;
  }
});

// node_modules/lodash/_nativeKeysIn.js
var require_nativeKeysIn = __commonJS({
  "node_modules/lodash/_nativeKeysIn.js"(exports, module) {
    function nativeKeysIn(object) {
      var result = [];
      if (object != null) {
        for (var key in Object(object)) {
          result.push(key);
        }
      }
      return result;
    }
    module.exports = nativeKeysIn;
  }
});

// node_modules/lodash/_baseKeysIn.js
var require_baseKeysIn = __commonJS({
  "node_modules/lodash/_baseKeysIn.js"(exports, module) {
    var isObject = require_isObject();
    var isPrototype = require_isPrototype();
    var nativeKeysIn = require_nativeKeysIn();
    var objectProto = Object.prototype;
    var hasOwnProperty = objectProto.hasOwnProperty;
    function baseKeysIn(object) {
      if (!isObject(object)) {
        return nativeKeysIn(object);
      }
      var isProto = isPrototype(object), result = [];
      for (var key in object) {
        if (!(key == "constructor" && (isProto || !hasOwnProperty.call(object, key)))) {
          result.push(key);
        }
      }
      return result;
    }
    module.exports = baseKeysIn;
  }
});

// node_modules/lodash/keysIn.js
var require_keysIn = __commonJS({
  "node_modules/lodash/keysIn.js"(exports, module) {
    var arrayLikeKeys = require_arrayLikeKeys();
    var baseKeysIn = require_baseKeysIn();
    var isArrayLike = require_isArrayLike();
    function keysIn(object) {
      return isArrayLike(object) ? arrayLikeKeys(object, true) : baseKeysIn(object);
    }
    module.exports = keysIn;
  }
});

// node_modules/lodash/defaults.js
var require_defaults = __commonJS({
  "node_modules/lodash/defaults.js"(exports, module) {
    var baseRest = require_baseRest();
    var eq = require_eq();
    var isIterateeCall = require_isIterateeCall();
    var keysIn = require_keysIn();
    var objectProto = Object.prototype;
    var hasOwnProperty = objectProto.hasOwnProperty;
    var defaults = baseRest(function(object, sources) {
      object = Object(object);
      var index = -1;
      var length = sources.length;
      var guard = length > 2 ? sources[2] : void 0;
      if (guard && isIterateeCall(sources[0], sources[1], guard)) {
        length = 1;
      }
      while (++index < length) {
        var source = sources[index];
        var props = keysIn(source);
        var propsIndex = -1;
        var propsLength = props.length;
        while (++propsIndex < propsLength) {
          var key = props[propsIndex];
          var value = object[key];
          if (value === void 0 || eq(value, objectProto[key]) && !hasOwnProperty.call(object, key)) {
            object[key] = source[key];
          }
        }
      }
      return object;
    });
    module.exports = defaults;
  }
});

// node_modules/lodash/isEmpty.js
var require_isEmpty = __commonJS({
  "node_modules/lodash/isEmpty.js"(exports, module) {
    var baseKeys = require_baseKeys();
    var getTag = require_getTag();
    var isArguments = require_isArguments();
    var isArray = require_isArray();
    var isArrayLike = require_isArrayLike();
    var isBuffer = require_isBuffer();
    var isPrototype = require_isPrototype();
    var isTypedArray = require_isTypedArray();
    var mapTag = "[object Map]";
    var setTag = "[object Set]";
    var objectProto = Object.prototype;
    var hasOwnProperty = objectProto.hasOwnProperty;
    function isEmpty(value) {
      if (value == null) {
        return true;
      }
      if (isArrayLike(value) && (isArray(value) || typeof value == "string" || typeof value.splice == "function" || isBuffer(value) || isTypedArray(value) || isArguments(value))) {
        return !value.length;
      }
      var tag = getTag(value);
      if (tag == mapTag || tag == setTag) {
        return !value.size;
      }
      if (isPrototype(value)) {
        return !baseKeys(value).length;
      }
      for (var key in value) {
        if (hasOwnProperty.call(value, key)) {
          return false;
        }
      }
      return true;
    }
    module.exports = isEmpty;
  }
});

// node_modules/react-fast-compare/index.js
var require_react_fast_compare = __commonJS({
  "node_modules/react-fast-compare/index.js"(exports, module) {
    var hasElementType = typeof Element !== "undefined";
    var hasMap = typeof Map === "function";
    var hasSet = typeof Set === "function";
    var hasArrayBuffer = typeof ArrayBuffer === "function" && !!ArrayBuffer.isView;
    function equal(a, b) {
      if (a === b) return true;
      if (a && b && typeof a == "object" && typeof b == "object") {
        if (a.constructor !== b.constructor) return false;
        var length, i, keys;
        if (Array.isArray(a)) {
          length = a.length;
          if (length != b.length) return false;
          for (i = length; i-- !== 0; )
            if (!equal(a[i], b[i])) return false;
          return true;
        }
        var it;
        if (hasMap && a instanceof Map && b instanceof Map) {
          if (a.size !== b.size) return false;
          it = a.entries();
          while (!(i = it.next()).done)
            if (!b.has(i.value[0])) return false;
          it = a.entries();
          while (!(i = it.next()).done)
            if (!equal(i.value[1], b.get(i.value[0]))) return false;
          return true;
        }
        if (hasSet && a instanceof Set && b instanceof Set) {
          if (a.size !== b.size) return false;
          it = a.entries();
          while (!(i = it.next()).done)
            if (!b.has(i.value[0])) return false;
          return true;
        }
        if (hasArrayBuffer && ArrayBuffer.isView(a) && ArrayBuffer.isView(b)) {
          length = a.length;
          if (length != b.length) return false;
          for (i = length; i-- !== 0; )
            if (a[i] !== b[i]) return false;
          return true;
        }
        if (a.constructor === RegExp) return a.source === b.source && a.flags === b.flags;
        if (a.valueOf !== Object.prototype.valueOf && typeof a.valueOf === "function" && typeof b.valueOf === "function") return a.valueOf() === b.valueOf();
        if (a.toString !== Object.prototype.toString && typeof a.toString === "function" && typeof b.toString === "function") return a.toString() === b.toString();
        keys = Object.keys(a);
        length = keys.length;
        if (length !== Object.keys(b).length) return false;
        for (i = length; i-- !== 0; )
          if (!Object.prototype.hasOwnProperty.call(b, keys[i])) return false;
        if (hasElementType && a instanceof Element) return false;
        for (i = length; i-- !== 0; ) {
          if ((keys[i] === "_owner" || keys[i] === "__v" || keys[i] === "__o") && a.$$typeof) {
            continue;
          }
          if (!equal(a[keys[i]], b[keys[i]])) return false;
        }
        return true;
      }
      return a !== a && b !== b;
    }
    module.exports = function isEqual15(a, b) {
      try {
        return equal(a, b);
      } catch (error) {
        if ((error.message || "").match(/stack|recursion/i)) {
          console.warn("react-fast-compare cannot handle circular refs");
          return false;
        }
        throw error;
      }
    };
  }
});

// node_modules/lodash/_baseFindIndex.js
var require_baseFindIndex = __commonJS({
  "node_modules/lodash/_baseFindIndex.js"(exports, module) {
    function baseFindIndex(array, predicate, fromIndex, fromRight) {
      var length = array.length, index = fromIndex + (fromRight ? 1 : -1);
      while (fromRight ? index-- : ++index < length) {
        if (predicate(array[index], index, array)) {
          return index;
        }
      }
      return -1;
    }
    module.exports = baseFindIndex;
  }
});

// node_modules/lodash/_baseIsNaN.js
var require_baseIsNaN = __commonJS({
  "node_modules/lodash/_baseIsNaN.js"(exports, module) {
    function baseIsNaN(value) {
      return value !== value;
    }
    module.exports = baseIsNaN;
  }
});

// node_modules/lodash/_strictIndexOf.js
var require_strictIndexOf = __commonJS({
  "node_modules/lodash/_strictIndexOf.js"(exports, module) {
    function strictIndexOf(array, value, fromIndex) {
      var index = fromIndex - 1, length = array.length;
      while (++index < length) {
        if (array[index] === value) {
          return index;
        }
      }
      return -1;
    }
    module.exports = strictIndexOf;
  }
});

// node_modules/lodash/_baseIndexOf.js
var require_baseIndexOf = __commonJS({
  "node_modules/lodash/_baseIndexOf.js"(exports, module) {
    var baseFindIndex = require_baseFindIndex();
    var baseIsNaN = require_baseIsNaN();
    var strictIndexOf = require_strictIndexOf();
    function baseIndexOf(array, value, fromIndex) {
      return value === value ? strictIndexOf(array, value, fromIndex) : baseFindIndex(array, baseIsNaN, fromIndex);
    }
    module.exports = baseIndexOf;
  }
});

// node_modules/lodash/_arrayIncludes.js
var require_arrayIncludes = __commonJS({
  "node_modules/lodash/_arrayIncludes.js"(exports, module) {
    var baseIndexOf = require_baseIndexOf();
    function arrayIncludes(array, value) {
      var length = array == null ? 0 : array.length;
      return !!length && baseIndexOf(array, value, 0) > -1;
    }
    module.exports = arrayIncludes;
  }
});

// node_modules/lodash/_arrayIncludesWith.js
var require_arrayIncludesWith = __commonJS({
  "node_modules/lodash/_arrayIncludesWith.js"(exports, module) {
    function arrayIncludesWith(array, value, comparator) {
      var index = -1, length = array == null ? 0 : array.length;
      while (++index < length) {
        if (comparator(value, array[index])) {
          return true;
        }
      }
      return false;
    }
    module.exports = arrayIncludesWith;
  }
});

// node_modules/lodash/noop.js
var require_noop = __commonJS({
  "node_modules/lodash/noop.js"(exports, module) {
    function noop() {
    }
    module.exports = noop;
  }
});

// node_modules/lodash/_createSet.js
var require_createSet = __commonJS({
  "node_modules/lodash/_createSet.js"(exports, module) {
    var Set2 = require_Set();
    var noop = require_noop();
    var setToArray = require_setToArray();
    var INFINITY = 1 / 0;
    var createSet = !(Set2 && 1 / setToArray(new Set2([, -0]))[1] == INFINITY) ? noop : function(values) {
      return new Set2(values);
    };
    module.exports = createSet;
  }
});

// node_modules/lodash/_baseUniq.js
var require_baseUniq = __commonJS({
  "node_modules/lodash/_baseUniq.js"(exports, module) {
    var SetCache = require_SetCache();
    var arrayIncludes = require_arrayIncludes();
    var arrayIncludesWith = require_arrayIncludesWith();
    var cacheHas = require_cacheHas();
    var createSet = require_createSet();
    var setToArray = require_setToArray();
    var LARGE_ARRAY_SIZE = 200;
    function baseUniq(array, iteratee, comparator) {
      var index = -1, includes = arrayIncludes, length = array.length, isCommon = true, result = [], seen = result;
      if (comparator) {
        isCommon = false;
        includes = arrayIncludesWith;
      } else if (length >= LARGE_ARRAY_SIZE) {
        var set = iteratee ? null : createSet(array);
        if (set) {
          return setToArray(set);
        }
        isCommon = false;
        includes = cacheHas;
        seen = new SetCache();
      } else {
        seen = iteratee ? [] : result;
      }
      outer:
        while (++index < length) {
          var value = array[index], computed = iteratee ? iteratee(value) : value;
          value = comparator || value !== 0 ? value : 0;
          if (isCommon && computed === computed) {
            var seenIndex = seen.length;
            while (seenIndex--) {
              if (seen[seenIndex] === computed) {
                continue outer;
              }
            }
            if (iteratee) {
              seen.push(computed);
            }
            result.push(value);
          } else if (!includes(seen, computed, comparator)) {
            if (seen !== result) {
              seen.push(computed);
            }
            result.push(value);
          }
        }
      return result;
    }
    module.exports = baseUniq;
  }
});

// node_modules/lodash/uniq.js
var require_uniq = __commonJS({
  "node_modules/lodash/uniq.js"(exports, module) {
    var baseUniq = require_baseUniq();
    function uniq(array) {
      return array && array.length ? baseUniq(array) : [];
    }
    module.exports = uniq;
  }
});

// node_modules/lodash/negate.js
var require_negate = __commonJS({
  "node_modules/lodash/negate.js"(exports, module) {
    var FUNC_ERROR_TEXT = "Expected a function";
    function negate(predicate) {
      if (typeof predicate != "function") {
        throw new TypeError(FUNC_ERROR_TEXT);
      }
      return function() {
        var args = arguments;
        switch (args.length) {
          case 0:
            return !predicate.call(this);
          case 1:
            return !predicate.call(this, args[0]);
          case 2:
            return !predicate.call(this, args[0], args[1]);
          case 3:
            return !predicate.call(this, args[0], args[1], args[2]);
        }
        return !predicate.apply(this, args);
      };
    }
    module.exports = negate;
  }
});

// node_modules/lodash/_getSymbolsIn.js
var require_getSymbolsIn = __commonJS({
  "node_modules/lodash/_getSymbolsIn.js"(exports, module) {
    var arrayPush = require_arrayPush();
    var getPrototype = require_getPrototype();
    var getSymbols = require_getSymbols();
    var stubArray = require_stubArray();
    var nativeGetSymbols = Object.getOwnPropertySymbols;
    var getSymbolsIn = !nativeGetSymbols ? stubArray : function(object) {
      var result = [];
      while (object) {
        arrayPush(result, getSymbols(object));
        object = getPrototype(object);
      }
      return result;
    };
    module.exports = getSymbolsIn;
  }
});

// node_modules/lodash/_getAllKeysIn.js
var require_getAllKeysIn = __commonJS({
  "node_modules/lodash/_getAllKeysIn.js"(exports, module) {
    var baseGetAllKeys = require_baseGetAllKeys();
    var getSymbolsIn = require_getSymbolsIn();
    var keysIn = require_keysIn();
    function getAllKeysIn(object) {
      return baseGetAllKeys(object, keysIn, getSymbolsIn);
    }
    module.exports = getAllKeysIn;
  }
});

// node_modules/lodash/pickBy.js
var require_pickBy = __commonJS({
  "node_modules/lodash/pickBy.js"(exports, module) {
    var arrayMap = require_arrayMap();
    var baseIteratee = require_baseIteratee();
    var basePickBy = require_basePickBy();
    var getAllKeysIn = require_getAllKeysIn();
    function pickBy(object, predicate) {
      if (object == null) {
        return {};
      }
      var props = arrayMap(getAllKeysIn(object), function(prop) {
        return [prop];
      });
      predicate = baseIteratee(predicate);
      return basePickBy(object, props, function(value, path) {
        return predicate(value, path[0]);
      });
    }
    module.exports = pickBy;
  }
});

// node_modules/lodash/omitBy.js
var require_omitBy = __commonJS({
  "node_modules/lodash/omitBy.js"(exports, module) {
    var baseIteratee = require_baseIteratee();
    var negate = require_negate();
    var pickBy = require_pickBy();
    function omitBy(object, predicate) {
      return pickBy(object, negate(baseIteratee(predicate)));
    }
    module.exports = omitBy;
  }
});

// node_modules/lodash/_baseIsDate.js
var require_baseIsDate = __commonJS({
  "node_modules/lodash/_baseIsDate.js"(exports, module) {
    var baseGetTag = require_baseGetTag();
    var isObjectLike = require_isObjectLike();
    var dateTag = "[object Date]";
    function baseIsDate(value) {
      return isObjectLike(value) && baseGetTag(value) == dateTag;
    }
    module.exports = baseIsDate;
  }
});

// node_modules/lodash/isDate.js
var require_isDate = __commonJS({
  "node_modules/lodash/isDate.js"(exports, module) {
    var baseIsDate = require_baseIsDate();
    var baseUnary = require_baseUnary();
    var nodeUtil = require_nodeUtil();
    var nodeIsDate = nodeUtil && nodeUtil.isDate;
    var isDate = nodeIsDate ? baseUnary(nodeIsDate) : baseIsDate;
    module.exports = isDate;
  }
});

// node_modules/lodash/_baseSortedUniq.js
var require_baseSortedUniq = __commonJS({
  "node_modules/lodash/_baseSortedUniq.js"(exports, module) {
    var eq = require_eq();
    function baseSortedUniq(array, iteratee) {
      var index = -1, length = array.length, resIndex = 0, result = [];
      while (++index < length) {
        var value = array[index], computed = iteratee ? iteratee(value) : value;
        if (!index || !eq(computed, seen)) {
          var seen = computed;
          result[resIndex++] = value === 0 ? 0 : value;
        }
      }
      return result;
    }
    module.exports = baseSortedUniq;
  }
});

// node_modules/lodash/sortedUniq.js
var require_sortedUniq = __commonJS({
  "node_modules/lodash/sortedUniq.js"(exports, module) {
    var baseSortedUniq = require_baseSortedUniq();
    function sortedUniq(array) {
      return array && array.length ? baseSortedUniq(array) : [];
    }
    module.exports = sortedUniq;
  }
});

// node_modules/lodash/isUndefined.js
var require_isUndefined = __commonJS({
  "node_modules/lodash/isUndefined.js"(exports, module) {
    function isUndefined(value) {
      return value === void 0;
    }
    module.exports = isUndefined;
  }
});

// node_modules/lodash/isEqual.js
var require_isEqual = __commonJS({
  "node_modules/lodash/isEqual.js"(exports, module) {
    var baseIsEqual = require_baseIsEqual();
    function isEqual15(value, other) {
      return baseIsEqual(value, other);
    }
    module.exports = isEqual15;
  }
});

// node_modules/lodash/uniqBy.js
var require_uniqBy = __commonJS({
  "node_modules/lodash/uniqBy.js"(exports, module) {
    var baseIteratee = require_baseIteratee();
    var baseUniq = require_baseUniq();
    function uniqBy(array, iteratee) {
      return array && array.length ? baseUniq(array, baseIteratee(iteratee, 2)) : [];
    }
    module.exports = uniqBy;
  }
});

// node_modules/lodash/_arrayAggregator.js
var require_arrayAggregator = __commonJS({
  "node_modules/lodash/_arrayAggregator.js"(exports, module) {
    function arrayAggregator(array, setter, iteratee, accumulator) {
      var index = -1, length = array == null ? 0 : array.length;
      while (++index < length) {
        var value = array[index];
        setter(accumulator, value, iteratee(value), array);
      }
      return accumulator;
    }
    module.exports = arrayAggregator;
  }
});

// node_modules/lodash/_baseAggregator.js
var require_baseAggregator = __commonJS({
  "node_modules/lodash/_baseAggregator.js"(exports, module) {
    var baseEach = require_baseEach();
    function baseAggregator(collection, setter, iteratee, accumulator) {
      baseEach(collection, function(value, key, collection2) {
        setter(accumulator, value, iteratee(value), collection2);
      });
      return accumulator;
    }
    module.exports = baseAggregator;
  }
});

// node_modules/lodash/_createAggregator.js
var require_createAggregator = __commonJS({
  "node_modules/lodash/_createAggregator.js"(exports, module) {
    var arrayAggregator = require_arrayAggregator();
    var baseAggregator = require_baseAggregator();
    var baseIteratee = require_baseIteratee();
    var isArray = require_isArray();
    function createAggregator(setter, initializer) {
      return function(collection, iteratee) {
        var func = isArray(collection) ? arrayAggregator : baseAggregator, accumulator = initializer ? initializer() : {};
        return func(collection, setter, baseIteratee(iteratee, 2), accumulator);
      };
    }
    module.exports = createAggregator;
  }
});

// node_modules/lodash/groupBy.js
var require_groupBy = __commonJS({
  "node_modules/lodash/groupBy.js"(exports, module) {
    var baseAssignValue = require_baseAssignValue();
    var createAggregator = require_createAggregator();
    var objectProto = Object.prototype;
    var hasOwnProperty = objectProto.hasOwnProperty;
    var groupBy = createAggregator(function(result, value, key) {
      if (hasOwnProperty.call(result, key)) {
        result[key].push(value);
      } else {
        baseAssignValue(result, key, [value]);
      }
    });
    module.exports = groupBy;
  }
});

// node_modules/lodash/now.js
var require_now = __commonJS({
  "node_modules/lodash/now.js"(exports, module) {
    var root = require_root();
    var now2 = function() {
      return root.Date.now();
    };
    module.exports = now2;
  }
});

// node_modules/lodash/_trimmedEndIndex.js
var require_trimmedEndIndex = __commonJS({
  "node_modules/lodash/_trimmedEndIndex.js"(exports, module) {
    var reWhitespace = /\s/;
    function trimmedEndIndex(string) {
      var index = string.length;
      while (index-- && reWhitespace.test(string.charAt(index))) {
      }
      return index;
    }
    module.exports = trimmedEndIndex;
  }
});

// node_modules/lodash/_baseTrim.js
var require_baseTrim = __commonJS({
  "node_modules/lodash/_baseTrim.js"(exports, module) {
    var trimmedEndIndex = require_trimmedEndIndex();
    var reTrimStart = /^\s+/;
    function baseTrim(string) {
      return string ? string.slice(0, trimmedEndIndex(string) + 1).replace(reTrimStart, "") : string;
    }
    module.exports = baseTrim;
  }
});

// node_modules/lodash/toNumber.js
var require_toNumber = __commonJS({
  "node_modules/lodash/toNumber.js"(exports, module) {
    var baseTrim = require_baseTrim();
    var isObject = require_isObject();
    var isSymbol = require_isSymbol();
    var NAN = 0 / 0;
    var reIsBadHex = /^[-+]0x[0-9a-f]+$/i;
    var reIsBinary = /^0b[01]+$/i;
    var reIsOctal = /^0o[0-7]+$/i;
    var freeParseInt = parseInt;
    function toNumber(value) {
      if (typeof value == "number") {
        return value;
      }
      if (isSymbol(value)) {
        return NAN;
      }
      if (isObject(value)) {
        var other = typeof value.valueOf == "function" ? value.valueOf() : value;
        value = isObject(other) ? other + "" : other;
      }
      if (typeof value != "string") {
        return value === 0 ? value : +value;
      }
      value = baseTrim(value);
      var isBinary = reIsBinary.test(value);
      return isBinary || reIsOctal.test(value) ? freeParseInt(value.slice(2), isBinary ? 2 : 8) : reIsBadHex.test(value) ? NAN : +value;
    }
    module.exports = toNumber;
  }
});

// node_modules/lodash/debounce.js
var require_debounce = __commonJS({
  "node_modules/lodash/debounce.js"(exports, module) {
    var isObject = require_isObject();
    var now2 = require_now();
    var toNumber = require_toNumber();
    var FUNC_ERROR_TEXT = "Expected a function";
    var nativeMax = Math.max;
    var nativeMin = Math.min;
    function debounce(func, wait, options7) {
      var lastArgs, lastThis, maxWait, result, timerId, lastCallTime, lastInvokeTime = 0, leading = false, maxing = false, trailing = true;
      if (typeof func != "function") {
        throw new TypeError(FUNC_ERROR_TEXT);
      }
      wait = toNumber(wait) || 0;
      if (isObject(options7)) {
        leading = !!options7.leading;
        maxing = "maxWait" in options7;
        maxWait = maxing ? nativeMax(toNumber(options7.maxWait) || 0, wait) : maxWait;
        trailing = "trailing" in options7 ? !!options7.trailing : trailing;
      }
      function invokeFunc(time2) {
        var args = lastArgs, thisArg = lastThis;
        lastArgs = lastThis = void 0;
        lastInvokeTime = time2;
        result = func.apply(thisArg, args);
        return result;
      }
      function leadingEdge(time2) {
        lastInvokeTime = time2;
        timerId = setTimeout(timerExpired, wait);
        return leading ? invokeFunc(time2) : result;
      }
      function remainingWait(time2) {
        var timeSinceLastCall = time2 - lastCallTime, timeSinceLastInvoke = time2 - lastInvokeTime, timeWaiting = wait - timeSinceLastCall;
        return maxing ? nativeMin(timeWaiting, maxWait - timeSinceLastInvoke) : timeWaiting;
      }
      function shouldInvoke(time2) {
        var timeSinceLastCall = time2 - lastCallTime, timeSinceLastInvoke = time2 - lastInvokeTime;
        return lastCallTime === void 0 || timeSinceLastCall >= wait || timeSinceLastCall < 0 || maxing && timeSinceLastInvoke >= maxWait;
      }
      function timerExpired() {
        var time2 = now2();
        if (shouldInvoke(time2)) {
          return trailingEdge(time2);
        }
        timerId = setTimeout(timerExpired, remainingWait(time2));
      }
      function trailingEdge(time2) {
        timerId = void 0;
        if (trailing && lastArgs) {
          return invokeFunc(time2);
        }
        lastArgs = lastThis = void 0;
        return result;
      }
      function cancel() {
        if (timerId !== void 0) {
          clearTimeout(timerId);
        }
        lastInvokeTime = 0;
        lastArgs = lastCallTime = lastThis = timerId = void 0;
      }
      function flush() {
        return timerId === void 0 ? result : trailingEdge(now2());
      }
      function debounced() {
        var time2 = now2(), isInvoking = shouldInvoke(time2);
        lastArgs = arguments;
        lastThis = this;
        lastCallTime = time2;
        if (isInvoking) {
          if (timerId === void 0) {
            return leadingEdge(lastCallTime);
          }
          if (maxing) {
            clearTimeout(timerId);
            timerId = setTimeout(timerExpired, wait);
            return invokeFunc(lastCallTime);
          }
        }
        if (timerId === void 0) {
          timerId = setTimeout(timerExpired, wait);
        }
        return result;
      }
      debounced.cancel = cancel;
      debounced.flush = flush;
      return debounced;
    }
    module.exports = debounce;
  }
});

// node_modules/lodash/throttle.js
var require_throttle = __commonJS({
  "node_modules/lodash/throttle.js"(exports, module) {
    var debounce = require_debounce();
    var isObject = require_isObject();
    var FUNC_ERROR_TEXT = "Expected a function";
    function throttle(func, wait, options7) {
      var leading = true, trailing = true;
      if (typeof func != "function") {
        throw new TypeError(FUNC_ERROR_TEXT);
      }
      if (isObject(options7)) {
        leading = "leading" in options7 ? !!options7.leading : leading;
        trailing = "trailing" in options7 ? !!options7.trailing : trailing;
      }
      return debounce(func, wait, {
        "leading": leading,
        "maxWait": wait,
        "trailing": trailing
      });
    }
    module.exports = throttle;
  }
});

// node_modules/lodash/fromPairs.js
var require_fromPairs = __commonJS({
  "node_modules/lodash/fromPairs.js"(exports, module) {
    function fromPairs(pairs) {
      var index = -1, length = pairs == null ? 0 : pairs.length, result = {};
      while (++index < length) {
        var pair = pairs[index];
        result[pair[0]] = pair[1];
      }
      return result;
    }
    module.exports = fromPairs;
  }
});

// node_modules/json-stringify-safe/stringify.js
var require_stringify = __commonJS({
  "node_modules/json-stringify-safe/stringify.js"(exports, module) {
    exports = module.exports = stringify2;
    exports.getSerialize = serializer;
    function stringify2(obj, replacer, spaces, cycleReplacer) {
      return JSON.stringify(obj, serializer(replacer, cycleReplacer), spaces);
    }
    function serializer(replacer, cycleReplacer) {
      var stack = [], keys = [];
      if (cycleReplacer == null) cycleReplacer = function(key, value) {
        if (stack[0] === value) return "[Circular ~]";
        return "[Circular ~." + keys.slice(0, stack.indexOf(value)).join(".") + "]";
      };
      return function(key, value) {
        if (stack.length > 0) {
          var thisPos = stack.indexOf(this);
          ~thisPos ? stack.splice(thisPos + 1) : stack.push(this);
          ~thisPos ? keys.splice(thisPos, Infinity, key) : keys.push(key);
          if (~stack.indexOf(value)) value = cycleReplacer.call(this, key, value);
        } else stack.push(value);
        return replacer == null ? value : replacer.call(this, key, value);
      };
    }
  }
});

// node_modules/lodash/_baseToPairs.js
var require_baseToPairs = __commonJS({
  "node_modules/lodash/_baseToPairs.js"(exports, module) {
    var arrayMap = require_arrayMap();
    function baseToPairs(object, props) {
      return arrayMap(props, function(key) {
        return [key, object[key]];
      });
    }
    module.exports = baseToPairs;
  }
});

// node_modules/lodash/_setToPairs.js
var require_setToPairs = __commonJS({
  "node_modules/lodash/_setToPairs.js"(exports, module) {
    function setToPairs(set) {
      var index = -1, result = Array(set.size);
      set.forEach(function(value) {
        result[++index] = [value, value];
      });
      return result;
    }
    module.exports = setToPairs;
  }
});

// node_modules/lodash/_createToPairs.js
var require_createToPairs = __commonJS({
  "node_modules/lodash/_createToPairs.js"(exports, module) {
    var baseToPairs = require_baseToPairs();
    var getTag = require_getTag();
    var mapToArray = require_mapToArray();
    var setToPairs = require_setToPairs();
    var mapTag = "[object Map]";
    var setTag = "[object Set]";
    function createToPairs(keysFunc) {
      return function(object) {
        var tag = getTag(object);
        if (tag == mapTag) {
          return mapToArray(object);
        }
        if (tag == setTag) {
          return setToPairs(object);
        }
        return baseToPairs(object, keysFunc(object));
      };
    }
    module.exports = createToPairs;
  }
});

// node_modules/lodash/toPairs.js
var require_toPairs = __commonJS({
  "node_modules/lodash/toPairs.js"(exports, module) {
    var createToPairs = require_createToPairs();
    var keys = require_keys();
    var toPairs = createToPairs(keys);
    module.exports = toPairs;
  }
});

// node_modules/lodash/_castFunction.js
var require_castFunction = __commonJS({
  "node_modules/lodash/_castFunction.js"(exports, module) {
    var identity4 = require_identity();
    function castFunction(value) {
      return typeof value == "function" ? value : identity4;
    }
    module.exports = castFunction;
  }
});

// node_modules/lodash/forOwn.js
var require_forOwn = __commonJS({
  "node_modules/lodash/forOwn.js"(exports, module) {
    var baseForOwn = require_baseForOwn();
    var castFunction = require_castFunction();
    function forOwn(object, iteratee) {
      return object && baseForOwn(object, castFunction(iteratee));
    }
    module.exports = forOwn;
  }
});

// node_modules/lodash/_baseDelay.js
var require_baseDelay = __commonJS({
  "node_modules/lodash/_baseDelay.js"(exports, module) {
    var FUNC_ERROR_TEXT = "Expected a function";
    function baseDelay(func, wait, args) {
      if (typeof func != "function") {
        throw new TypeError(FUNC_ERROR_TEXT);
      }
      return setTimeout(function() {
        func.apply(void 0, args);
      }, wait);
    }
    module.exports = baseDelay;
  }
});

// node_modules/lodash/delay.js
var require_delay = __commonJS({
  "node_modules/lodash/delay.js"(exports, module) {
    var baseDelay = require_baseDelay();
    var baseRest = require_baseRest();
    var toNumber = require_toNumber();
    var delay = baseRest(function(func, wait, args) {
      return baseDelay(func, toNumber(wait) || 0, args);
    });
    module.exports = delay;
  }
});

// node_modules/lodash/_baseIsRegExp.js
var require_baseIsRegExp = __commonJS({
  "node_modules/lodash/_baseIsRegExp.js"(exports, module) {
    var baseGetTag = require_baseGetTag();
    var isObjectLike = require_isObjectLike();
    var regexpTag = "[object RegExp]";
    function baseIsRegExp(value) {
      return isObjectLike(value) && baseGetTag(value) == regexpTag;
    }
    module.exports = baseIsRegExp;
  }
});

// node_modules/lodash/isRegExp.js
var require_isRegExp = __commonJS({
  "node_modules/lodash/isRegExp.js"(exports, module) {
    var baseIsRegExp = require_baseIsRegExp();
    var baseUnary = require_baseUnary();
    var nodeUtil = require_nodeUtil();
    var nodeIsRegExp = nodeUtil && nodeUtil.isRegExp;
    var isRegExp = nodeIsRegExp ? baseUnary(nodeIsRegExp) : baseIsRegExp;
    module.exports = isRegExp;
  }
});

// node_modules/delaunator/delaunator.js
var require_delaunator = __commonJS({
  "node_modules/delaunator/delaunator.js"(exports, module) {
    (function(global2, factory) {
      typeof exports === "object" && typeof module !== "undefined" ? module.exports = factory() : typeof define === "function" && define.amd ? define(factory) : (global2 = global2 || self, global2.Delaunator = factory());
    })(exports, function() {
      "use strict";
      var EPSILON = Math.pow(2, -52);
      var EDGE_STACK = new Uint32Array(512);
      var Delaunator = function Delaunator2(coords) {
        var n = coords.length >> 1;
        if (n > 0 && typeof coords[0] !== "number") {
          throw new Error("Expected coords to contain numbers.");
        }
        this.coords = coords;
        var maxTriangles = Math.max(2 * n - 5, 0);
        this._triangles = new Uint32Array(maxTriangles * 3);
        this._halfedges = new Int32Array(maxTriangles * 3);
        this._hashSize = Math.ceil(Math.sqrt(n));
        this._hullPrev = new Uint32Array(n);
        this._hullNext = new Uint32Array(n);
        this._hullTri = new Uint32Array(n);
        this._hullHash = new Int32Array(this._hashSize).fill(-1);
        this._ids = new Uint32Array(n);
        this._dists = new Float64Array(n);
        this.update();
      };
      Delaunator.from = function from(points, getX, getY) {
        if (getX === void 0) getX = defaultGetX;
        if (getY === void 0) getY = defaultGetY;
        var n = points.length;
        var coords = new Float64Array(n * 2);
        for (var i = 0; i < n; i++) {
          var p = points[i];
          coords[2 * i] = getX(p);
          coords[2 * i + 1] = getY(p);
        }
        return new Delaunator(coords);
      };
      Delaunator.prototype.update = function update() {
        var ref = this;
        var coords = ref.coords;
        var hullPrev = ref._hullPrev;
        var hullNext = ref._hullNext;
        var hullTri = ref._hullTri;
        var hullHash = ref._hullHash;
        var n = coords.length >> 1;
        var minX = Infinity;
        var minY = Infinity;
        var maxX = -Infinity;
        var maxY = -Infinity;
        for (var i = 0; i < n; i++) {
          var x2 = coords[2 * i];
          var y2 = coords[2 * i + 1];
          if (x2 < minX) {
            minX = x2;
          }
          if (y2 < minY) {
            minY = y2;
          }
          if (x2 > maxX) {
            maxX = x2;
          }
          if (y2 > maxY) {
            maxY = y2;
          }
          this._ids[i] = i;
        }
        var cx = (minX + maxX) / 2;
        var cy = (minY + maxY) / 2;
        var minDist = Infinity;
        var i0, i1, i2;
        for (var i$1 = 0; i$1 < n; i$1++) {
          var d = dist(cx, cy, coords[2 * i$1], coords[2 * i$1 + 1]);
          if (d < minDist) {
            i0 = i$1;
            minDist = d;
          }
        }
        var i0x = coords[2 * i0];
        var i0y = coords[2 * i0 + 1];
        minDist = Infinity;
        for (var i$2 = 0; i$2 < n; i$2++) {
          if (i$2 === i0) {
            continue;
          }
          var d$1 = dist(i0x, i0y, coords[2 * i$2], coords[2 * i$2 + 1]);
          if (d$1 < minDist && d$1 > 0) {
            i1 = i$2;
            minDist = d$1;
          }
        }
        var i1x = coords[2 * i1];
        var i1y = coords[2 * i1 + 1];
        var minRadius = Infinity;
        for (var i$3 = 0; i$3 < n; i$3++) {
          if (i$3 === i0 || i$3 === i1) {
            continue;
          }
          var r = circumradius(i0x, i0y, i1x, i1y, coords[2 * i$3], coords[2 * i$3 + 1]);
          if (r < minRadius) {
            i2 = i$3;
            minRadius = r;
          }
        }
        var i2x = coords[2 * i2];
        var i2y = coords[2 * i2 + 1];
        if (minRadius === Infinity) {
          for (var i$4 = 0; i$4 < n; i$4++) {
            this._dists[i$4] = coords[2 * i$4] - coords[0] || coords[2 * i$4 + 1] - coords[1];
          }
          quicksort(this._ids, this._dists, 0, n - 1);
          var hull = new Uint32Array(n);
          var j = 0;
          for (var i$5 = 0, d0 = -Infinity; i$5 < n; i$5++) {
            var id = this._ids[i$5];
            if (this._dists[id] > d0) {
              hull[j++] = id;
              d0 = this._dists[id];
            }
          }
          this.hull = hull.subarray(0, j);
          this.triangles = new Uint32Array(0);
          this.halfedges = new Uint32Array(0);
          return;
        }
        if (orient(i0x, i0y, i1x, i1y, i2x, i2y)) {
          var i$6 = i1;
          var x$1 = i1x;
          var y$1 = i1y;
          i1 = i2;
          i1x = i2x;
          i1y = i2y;
          i2 = i$6;
          i2x = x$1;
          i2y = y$1;
        }
        var center = circumcenter(i0x, i0y, i1x, i1y, i2x, i2y);
        this._cx = center.x;
        this._cy = center.y;
        for (var i$7 = 0; i$7 < n; i$7++) {
          this._dists[i$7] = dist(coords[2 * i$7], coords[2 * i$7 + 1], center.x, center.y);
        }
        quicksort(this._ids, this._dists, 0, n - 1);
        this._hullStart = i0;
        var hullSize = 3;
        hullNext[i0] = hullPrev[i2] = i1;
        hullNext[i1] = hullPrev[i0] = i2;
        hullNext[i2] = hullPrev[i1] = i0;
        hullTri[i0] = 0;
        hullTri[i1] = 1;
        hullTri[i2] = 2;
        hullHash.fill(-1);
        hullHash[this._hashKey(i0x, i0y)] = i0;
        hullHash[this._hashKey(i1x, i1y)] = i1;
        hullHash[this._hashKey(i2x, i2y)] = i2;
        this.trianglesLen = 0;
        this._addTriangle(i0, i1, i2, -1, -1, -1);
        for (var k = 0, xp = void 0, yp = void 0; k < this._ids.length; k++) {
          var i$8 = this._ids[k];
          var x$2 = coords[2 * i$8];
          var y$2 = coords[2 * i$8 + 1];
          if (k > 0 && Math.abs(x$2 - xp) <= EPSILON && Math.abs(y$2 - yp) <= EPSILON) {
            continue;
          }
          xp = x$2;
          yp = y$2;
          if (i$8 === i0 || i$8 === i1 || i$8 === i2) {
            continue;
          }
          var start = 0;
          for (var j$1 = 0, key = this._hashKey(x$2, y$2); j$1 < this._hashSize; j$1++) {
            start = hullHash[(key + j$1) % this._hashSize];
            if (start !== -1 && start !== hullNext[start]) {
              break;
            }
          }
          start = hullPrev[start];
          var e = start, q = void 0;
          while (q = hullNext[e], !orient(x$2, y$2, coords[2 * e], coords[2 * e + 1], coords[2 * q], coords[2 * q + 1])) {
            e = q;
            if (e === start) {
              e = -1;
              break;
            }
          }
          if (e === -1) {
            continue;
          }
          var t = this._addTriangle(e, i$8, hullNext[e], -1, -1, hullTri[e]);
          hullTri[i$8] = this._legalize(t + 2);
          hullTri[e] = t;
          hullSize++;
          var n$1 = hullNext[e];
          while (q = hullNext[n$1], orient(x$2, y$2, coords[2 * n$1], coords[2 * n$1 + 1], coords[2 * q], coords[2 * q + 1])) {
            t = this._addTriangle(n$1, i$8, q, hullTri[i$8], -1, hullTri[n$1]);
            hullTri[i$8] = this._legalize(t + 2);
            hullNext[n$1] = n$1;
            hullSize--;
            n$1 = q;
          }
          if (e === start) {
            while (q = hullPrev[e], orient(x$2, y$2, coords[2 * q], coords[2 * q + 1], coords[2 * e], coords[2 * e + 1])) {
              t = this._addTriangle(q, i$8, e, -1, hullTri[e], hullTri[q]);
              this._legalize(t + 2);
              hullTri[q] = t;
              hullNext[e] = e;
              hullSize--;
              e = q;
            }
          }
          this._hullStart = hullPrev[i$8] = e;
          hullNext[e] = hullPrev[n$1] = i$8;
          hullNext[i$8] = n$1;
          hullHash[this._hashKey(x$2, y$2)] = i$8;
          hullHash[this._hashKey(coords[2 * e], coords[2 * e + 1])] = e;
        }
        this.hull = new Uint32Array(hullSize);
        for (var i$9 = 0, e$1 = this._hullStart; i$9 < hullSize; i$9++) {
          this.hull[i$9] = e$1;
          e$1 = hullNext[e$1];
        }
        this.triangles = this._triangles.subarray(0, this.trianglesLen);
        this.halfedges = this._halfedges.subarray(0, this.trianglesLen);
      };
      Delaunator.prototype._hashKey = function _hashKey(x2, y2) {
        return Math.floor(pseudoAngle(x2 - this._cx, y2 - this._cy) * this._hashSize) % this._hashSize;
      };
      Delaunator.prototype._legalize = function _legalize(a) {
        var ref = this;
        var triangles = ref._triangles;
        var halfedges = ref._halfedges;
        var coords = ref.coords;
        var i = 0;
        var ar = 0;
        while (true) {
          var b = halfedges[a];
          var a0 = a - a % 3;
          ar = a0 + (a + 2) % 3;
          if (b === -1) {
            if (i === 0) {
              break;
            }
            a = EDGE_STACK[--i];
            continue;
          }
          var b02 = b - b % 3;
          var al = a0 + (a + 1) % 3;
          var bl = b02 + (b + 2) % 3;
          var p0 = triangles[ar];
          var pr = triangles[a];
          var pl = triangles[al];
          var p1 = triangles[bl];
          var illegal = inCircle(
            coords[2 * p0],
            coords[2 * p0 + 1],
            coords[2 * pr],
            coords[2 * pr + 1],
            coords[2 * pl],
            coords[2 * pl + 1],
            coords[2 * p1],
            coords[2 * p1 + 1]
          );
          if (illegal) {
            triangles[a] = p1;
            triangles[b] = p0;
            var hbl = halfedges[bl];
            if (hbl === -1) {
              var e = this._hullStart;
              do {
                if (this._hullTri[e] === bl) {
                  this._hullTri[e] = a;
                  break;
                }
                e = this._hullPrev[e];
              } while (e !== this._hullStart);
            }
            this._link(a, hbl);
            this._link(b, halfedges[ar]);
            this._link(ar, bl);
            var br = b02 + (b + 1) % 3;
            if (i < EDGE_STACK.length) {
              EDGE_STACK[i++] = br;
            }
          } else {
            if (i === 0) {
              break;
            }
            a = EDGE_STACK[--i];
          }
        }
        return ar;
      };
      Delaunator.prototype._link = function _link(a, b) {
        this._halfedges[a] = b;
        if (b !== -1) {
          this._halfedges[b] = a;
        }
      };
      Delaunator.prototype._addTriangle = function _addTriangle(i0, i1, i2, a, b, c) {
        var t = this.trianglesLen;
        this._triangles[t] = i0;
        this._triangles[t + 1] = i1;
        this._triangles[t + 2] = i2;
        this._link(t, a);
        this._link(t + 1, b);
        this._link(t + 2, c);
        this.trianglesLen += 3;
        return t;
      };
      function pseudoAngle(dx, dy) {
        var p = dx / (Math.abs(dx) + Math.abs(dy));
        return (dy > 0 ? 3 - p : 1 + p) / 4;
      }
      function dist(ax, ay, bx, by) {
        var dx = ax - bx;
        var dy = ay - by;
        return dx * dx + dy * dy;
      }
      function orientIfSure(px, py, rx, ry, qx, qy) {
        var l = (ry - py) * (qx - px);
        var r = (rx - px) * (qy - py);
        return Math.abs(l - r) >= 33306690738754716e-32 * Math.abs(l + r) ? l - r : 0;
      }
      function orient(rx, ry, qx, qy, px, py) {
        var sign = orientIfSure(px, py, rx, ry, qx, qy) || orientIfSure(rx, ry, qx, qy, px, py) || orientIfSure(qx, qy, px, py, rx, ry);
        return sign < 0;
      }
      function inCircle(ax, ay, bx, by, cx, cy, px, py) {
        var dx = ax - px;
        var dy = ay - py;
        var ex = bx - px;
        var ey = by - py;
        var fx = cx - px;
        var fy = cy - py;
        var ap = dx * dx + dy * dy;
        var bp = ex * ex + ey * ey;
        var cp = fx * fx + fy * fy;
        return dx * (ey * cp - bp * fy) - dy * (ex * cp - bp * fx) + ap * (ex * fy - ey * fx) < 0;
      }
      function circumradius(ax, ay, bx, by, cx, cy) {
        var dx = bx - ax;
        var dy = by - ay;
        var ex = cx - ax;
        var ey = cy - ay;
        var bl = dx * dx + dy * dy;
        var cl = ex * ex + ey * ey;
        var d = 0.5 / (dx * ey - dy * ex);
        var x2 = (ey * bl - dy * cl) * d;
        var y2 = (dx * cl - ex * bl) * d;
        return x2 * x2 + y2 * y2;
      }
      function circumcenter(ax, ay, bx, by, cx, cy) {
        var dx = bx - ax;
        var dy = by - ay;
        var ex = cx - ax;
        var ey = cy - ay;
        var bl = dx * dx + dy * dy;
        var cl = ex * ex + ey * ey;
        var d = 0.5 / (dx * ey - dy * ex);
        var x2 = ax + (ey * bl - dy * cl) * d;
        var y2 = ay + (dx * cl - ex * bl) * d;
        return { x: x2, y: y2 };
      }
      function quicksort(ids, dists, left, right) {
        if (right - left <= 20) {
          for (var i = left + 1; i <= right; i++) {
            var temp = ids[i];
            var tempDist = dists[temp];
            var j = i - 1;
            while (j >= left && dists[ids[j]] > tempDist) {
              ids[j + 1] = ids[j--];
            }
            ids[j + 1] = temp;
          }
        } else {
          var median = left + right >> 1;
          var i$1 = left + 1;
          var j$1 = right;
          swap(ids, median, i$1);
          if (dists[ids[left]] > dists[ids[right]]) {
            swap(ids, left, right);
          }
          if (dists[ids[i$1]] > dists[ids[right]]) {
            swap(ids, i$1, right);
          }
          if (dists[ids[left]] > dists[ids[i$1]]) {
            swap(ids, left, i$1);
          }
          var temp$1 = ids[i$1];
          var tempDist$1 = dists[temp$1];
          while (true) {
            do {
              i$1++;
            } while (dists[ids[i$1]] < tempDist$1);
            do {
              j$1--;
            } while (dists[ids[j$1]] > tempDist$1);
            if (j$1 < i$1) {
              break;
            }
            swap(ids, i$1, j$1);
          }
          ids[left + 1] = ids[j$1];
          ids[j$1] = temp$1;
          if (right - i$1 + 1 >= j$1 - left) {
            quicksort(ids, dists, i$1, right);
            quicksort(ids, dists, left, j$1 - 1);
          } else {
            quicksort(ids, dists, left, j$1 - 1);
            quicksort(ids, dists, i$1, right);
          }
        }
      }
      function swap(arr, i, j) {
        var tmp = arr[i];
        arr[i] = arr[j];
        arr[j] = tmp;
      }
      function defaultGetX(p) {
        return p[0];
      }
      function defaultGetY(p) {
        return p[1];
      }
      return Delaunator;
    });
  }
});

// node_modules/delaunay-find/lib/index.js
var require_lib = __commonJS({
  "node_modules/delaunay-find/lib/index.js"(exports) {
    "use strict";
    exports.__esModule = true;
    exports["default"] = void 0;
    var _delaunator = _interopRequireDefault(require_delaunator());
    function _interopRequireDefault(obj) {
      return obj && obj.__esModule ? obj : { "default": obj };
    }
    function pointX(p) {
      return p[0];
    }
    function pointY(p) {
      return p[1];
    }
    function collinear(d) {
      var triangles = d.triangles, coords = d.coords;
      for (var i = 0; i < triangles.length; i += 3) {
        var a = 2 * triangles[i];
        var b = 2 * triangles[i + 1];
        var c = 2 * triangles[i + 2];
        var cross2 = (coords[c] - coords[a]) * (coords[b + 1] - coords[a + 1]) - (coords[b] - coords[a]) * (coords[c + 1] - coords[a + 1]);
        if (cross2 > 1e-10) {
          return false;
        }
      }
      return true;
    }
    function jitter(x2, y2, r) {
      return [x2 + Math.sin(x2 + y2) * r, y2 + Math.cos(x2 - y2) * r];
    }
    function flatArray(points, fx, fy, that) {
      var n = points.length;
      var array = new Float64Array(n * 2);
      for (var i = 0; i < n; ++i) {
        var p = points[i];
        array[i * 2] = fx.call(that, p, i, points);
        array[i * 2 + 1] = fy.call(that, p, i, points);
      }
      return array;
    }
    var Delaunay2 = function() {
      function Delaunay3(points) {
        var delaunator = new _delaunator["default"](points);
        this.inedges = new Int32Array(points.length / 2);
        this._hullIndex = new Int32Array(points.length / 2);
        this.points = delaunator.coords;
        this._init(delaunator);
      }
      var _proto = Delaunay3.prototype;
      _proto._init = function _init(delaunator) {
        var d = delaunator;
        var points = this.points;
        if (d.hull && d.hull.length > 2 && collinear(d)) {
          this.collinear = Int32Array.from({
            length: points.length / 2
          }, function(_, i2) {
            return i2;
          }).sort(function(i2, j) {
            return points[2 * i2] - points[2 * j] || points[2 * i2 + 1] - points[2 * j + 1];
          });
          var e = this.collinear[0];
          var f = this.collinear[this.collinear.length - 1];
          var bounds = [points[2 * e], points[2 * e + 1], points[2 * f], points[2 * f + 1]];
          var r = 1e-8 * // eslint-disable-line no-magic-numbers
          Math.sqrt(Math.pow(bounds[3] - bounds[1], 2) + Math.pow(bounds[2] - bounds[0], 2));
          for (var i = 0, n = points.length / 2; i < n; ++i) {
            var p = jitter(points[2 * i], points[2 * i + 1], r);
            points[2 * i] = p[0];
            points[2 * i + 1] = p[1];
          }
          delaunator = new _delaunator["default"](points);
        }
        var halfedges = this.halfedges = delaunator.halfedges;
        var hull = this.hull = delaunator.hull;
        var triangles = this.triangles = delaunator.triangles;
        var inedges = this.inedges.fill(-1);
        var hullIndex = this._hullIndex.fill(-1);
        for (var _e = 0, _n = halfedges.length; _e < _n; ++_e) {
          var _p = triangles[_e % 3 === 2 ? _e - 2 : _e + 1];
          if (halfedges[_e] === -1 || inedges[_p] === -1) inedges[_p] = _e;
        }
        for (var _i = 0, _n2 = hull.length; _i < _n2; ++_i) {
          hullIndex[hull[_i]] = _i;
        }
        if (hull.length <= 2 && hull.length > 0) {
          this.triangles = new Int32Array(3).fill(-1);
          this.halfedges = new Int32Array(3).fill(-1);
          this.triangles[0] = hull[0];
          this.triangles[1] = hull[1];
          this.triangles[2] = hull[1];
          inedges[hull[0]] = 1;
          if (hull.length === 2) inedges[hull[1]] = 0;
        }
      };
      _proto.neighbors = function neighbors(i) {
        var results = [];
        var inedges = this.inedges, hull = this.hull, _hullIndex = this._hullIndex, halfedges = this.halfedges, triangles = this.triangles;
        var e0 = inedges[i];
        if (e0 === -1) return results;
        var e = e0;
        var p0 = -1;
        do {
          p0 = triangles[e];
          results.push(p0);
          e = e % 3 === 2 ? e - 2 : e + 1;
          if (triangles[e] !== i) break;
          e = halfedges[e];
          if (e === -1) {
            var p = hull[(_hullIndex[i] + 1) % hull.length];
            if (p !== p0) results.push(p);
            break;
          }
        } while (e !== e0);
        return results;
      };
      _proto.find = function find(x2, y2, i) {
        if (i === void 0) {
          i = 0;
        }
        if ((x2 = +x2, x2 !== x2) || (y2 = +y2, y2 !== y2)) return -1;
        var i0 = i;
        var c;
        while ((c = this._step(i, x2, y2)) >= 0 && c !== i && c !== i0) {
          i = c;
        }
        return c;
      };
      _proto._step = function _step(i, x2, y2) {
        var inedges = this.inedges, points = this.points;
        if (inedges[i] === -1 || !points.length) return (i + 1) % (points.length >> 1);
        var c = i;
        var dc = Math.pow(x2 - points[i * 2], 2) + Math.pow(y2 - points[i * 2 + 1], 2);
        for (var _iterator = this.neighbors(i), _isArray = Array.isArray(_iterator), _i2 = 0, _iterator = _isArray ? _iterator : _iterator[Symbol.iterator](); ; ) {
          var _ref;
          if (_isArray) {
            if (_i2 >= _iterator.length) break;
            _ref = _iterator[_i2++];
          } else {
            _i2 = _iterator.next();
            if (_i2.done) break;
            _ref = _i2.value;
          }
          var t = _ref;
          var dt = Math.pow(x2 - points[t * 2], 2) + Math.pow(y2 - points[t * 2 + 1], 2);
          if (dt < dc) {
            dc = dt;
            c = t;
          }
        }
        return c;
      };
      return Delaunay3;
    }();
    exports["default"] = Delaunay2;
    Delaunay2.from = function(points, fx, fy, that) {
      if (fx === void 0) {
        fx = pointX;
      }
      if (fy === void 0) {
        fy = pointY;
      }
      return new Delaunay2(flatArray(points, fx, fy, that));
    };
  }
});

// node_modules/lodash/_copyObject.js
var require_copyObject = __commonJS({
  "node_modules/lodash/_copyObject.js"(exports, module) {
    var assignValue = require_assignValue();
    var baseAssignValue = require_baseAssignValue();
    function copyObject(source, props, object, customizer) {
      var isNew = !object;
      object || (object = {});
      var index = -1, length = props.length;
      while (++index < length) {
        var key = props[index];
        var newValue = customizer ? customizer(object[key], source[key], key, object, source) : void 0;
        if (newValue === void 0) {
          newValue = source[key];
        }
        if (isNew) {
          baseAssignValue(object, key, newValue);
        } else {
          assignValue(object, key, newValue);
        }
      }
      return object;
    }
    module.exports = copyObject;
  }
});

// node_modules/lodash/_createAssigner.js
var require_createAssigner = __commonJS({
  "node_modules/lodash/_createAssigner.js"(exports, module) {
    var baseRest = require_baseRest();
    var isIterateeCall = require_isIterateeCall();
    function createAssigner(assigner) {
      return baseRest(function(object, sources) {
        var index = -1, length = sources.length, customizer = length > 1 ? sources[length - 1] : void 0, guard = length > 2 ? sources[2] : void 0;
        customizer = assigner.length > 3 && typeof customizer == "function" ? (length--, customizer) : void 0;
        if (guard && isIterateeCall(sources[0], sources[1], guard)) {
          customizer = length < 3 ? void 0 : customizer;
          length = 1;
        }
        object = Object(object);
        while (++index < length) {
          var source = sources[index];
          if (source) {
            assigner(object, source, index, customizer);
          }
        }
        return object;
      });
    }
    module.exports = createAssigner;
  }
});

// node_modules/lodash/assign.js
var require_assign = __commonJS({
  "node_modules/lodash/assign.js"(exports, module) {
    var assignValue = require_assignValue();
    var copyObject = require_copyObject();
    var createAssigner = require_createAssigner();
    var isArrayLike = require_isArrayLike();
    var isPrototype = require_isPrototype();
    var keys = require_keys();
    var objectProto = Object.prototype;
    var hasOwnProperty = objectProto.hasOwnProperty;
    var assign = createAssigner(function(object, source) {
      if (isPrototype(source) || isArrayLike(source)) {
        copyObject(source, keys(source), object);
        return;
      }
      for (var key in source) {
        if (hasOwnProperty.call(source, key)) {
          assignValue(object, key, source[key]);
        }
      }
    });
    module.exports = assign;
  }
});

// node_modules/lodash/_baseRange.js
var require_baseRange = __commonJS({
  "node_modules/lodash/_baseRange.js"(exports, module) {
    var nativeCeil = Math.ceil;
    var nativeMax = Math.max;
    function baseRange(start, end, step, fromRight) {
      var index = -1, length = nativeMax(nativeCeil((end - start) / (step || 1)), 0), result = Array(length);
      while (length--) {
        result[fromRight ? length : ++index] = start;
        start += step;
      }
      return result;
    }
    module.exports = baseRange;
  }
});

// node_modules/lodash/toFinite.js
var require_toFinite = __commonJS({
  "node_modules/lodash/toFinite.js"(exports, module) {
    var toNumber = require_toNumber();
    var INFINITY = 1 / 0;
    var MAX_INTEGER = 17976931348623157e292;
    function toFinite(value) {
      if (!value) {
        return value === 0 ? value : 0;
      }
      value = toNumber(value);
      if (value === INFINITY || value === -INFINITY) {
        var sign = value < 0 ? -1 : 1;
        return sign * MAX_INTEGER;
      }
      return value === value ? value : 0;
    }
    module.exports = toFinite;
  }
});

// node_modules/lodash/_createRange.js
var require_createRange = __commonJS({
  "node_modules/lodash/_createRange.js"(exports, module) {
    var baseRange = require_baseRange();
    var isIterateeCall = require_isIterateeCall();
    var toFinite = require_toFinite();
    function createRange(fromRight) {
      return function(start, end, step) {
        if (step && typeof step != "number" && isIterateeCall(start, end, step)) {
          end = step = void 0;
        }
        start = toFinite(start);
        if (end === void 0) {
          end = start;
          start = 0;
        } else {
          end = toFinite(end);
        }
        step = step === void 0 ? start < end ? 1 : -1 : toFinite(step);
        return baseRange(start, end, step, fromRight);
      };
    }
    module.exports = createRange;
  }
});

// node_modules/lodash/range.js
var require_range = __commonJS({
  "node_modules/lodash/range.js"(exports, module) {
    var createRange = require_createRange();
    var range3 = createRange();
    module.exports = range3;
  }
});

// node_modules/victory-area/es/victory-area.js
var import_react35 = __toESM(require_react());

// node_modules/victory-core/es/victory-accessible-group/victory-accessible-group.js
var import_react = __toESM(require_react());
var VictoryAccessibleGroup = (_ref) => {
  let {
    desc,
    children,
    tabIndex,
    className = "VictoryAccessibleGroup",
    ...props
  } = _ref;
  const descId = desc && (props["aria-describedby"] || desc.split(" ").join("-"));
  return desc ? import_react.default.createElement("g", {
    "aria-label": props["aria-label"],
    "aria-describedby": descId,
    className,
    tabIndex
  }, import_react.default.createElement("desc", {
    id: descId
  }, desc), children) : import_react.default.createElement("g", {
    "aria-label": props["aria-label"],
    "aria-describedby": props["aria-describedby"],
    className,
    tabIndex
  }, children);
};

// node_modules/victory-core/es/victory-animation/victory-animation.js
var import_react3 = __toESM(require_react());

// node_modules/victory-core/node_modules/victory-vendor/es/d3-ease.js
var d3_ease_exports = {};
__export(d3_ease_exports, {
  easeBack: () => backInOut,
  easeBackIn: () => backIn,
  easeBackInOut: () => backInOut,
  easeBackOut: () => backOut,
  easeBounce: () => bounceOut,
  easeBounceIn: () => bounceIn,
  easeBounceInOut: () => bounceInOut,
  easeBounceOut: () => bounceOut,
  easeCircle: () => circleInOut,
  easeCircleIn: () => circleIn,
  easeCircleInOut: () => circleInOut,
  easeCircleOut: () => circleOut,
  easeCubic: () => cubicInOut,
  easeCubicIn: () => cubicIn,
  easeCubicInOut: () => cubicInOut,
  easeCubicOut: () => cubicOut,
  easeElastic: () => elasticOut,
  easeElasticIn: () => elasticIn,
  easeElasticInOut: () => elasticInOut,
  easeElasticOut: () => elasticOut,
  easeExp: () => expInOut,
  easeExpIn: () => expIn,
  easeExpInOut: () => expInOut,
  easeExpOut: () => expOut,
  easeLinear: () => linear,
  easePoly: () => polyInOut,
  easePolyIn: () => polyIn,
  easePolyInOut: () => polyInOut,
  easePolyOut: () => polyOut,
  easeQuad: () => quadInOut,
  easeQuadIn: () => quadIn,
  easeQuadInOut: () => quadInOut,
  easeQuadOut: () => quadOut,
  easeSin: () => sinInOut,
  easeSinIn: () => sinIn,
  easeSinInOut: () => sinInOut,
  easeSinOut: () => sinOut
});

// node_modules/d3-ease/src/linear.js
var linear = (t) => +t;

// node_modules/d3-ease/src/quad.js
function quadIn(t) {
  return t * t;
}
function quadOut(t) {
  return t * (2 - t);
}
function quadInOut(t) {
  return ((t *= 2) <= 1 ? t * t : --t * (2 - t) + 1) / 2;
}

// node_modules/d3-ease/src/cubic.js
function cubicIn(t) {
  return t * t * t;
}
function cubicOut(t) {
  return --t * t * t + 1;
}
function cubicInOut(t) {
  return ((t *= 2) <= 1 ? t * t * t : (t -= 2) * t * t + 2) / 2;
}

// node_modules/d3-ease/src/poly.js
var exponent = 3;
var polyIn = function custom(e) {
  e = +e;
  function polyIn2(t) {
    return Math.pow(t, e);
  }
  polyIn2.exponent = custom;
  return polyIn2;
}(exponent);
var polyOut = function custom2(e) {
  e = +e;
  function polyOut2(t) {
    return 1 - Math.pow(1 - t, e);
  }
  polyOut2.exponent = custom2;
  return polyOut2;
}(exponent);
var polyInOut = function custom3(e) {
  e = +e;
  function polyInOut2(t) {
    return ((t *= 2) <= 1 ? Math.pow(t, e) : 2 - Math.pow(2 - t, e)) / 2;
  }
  polyInOut2.exponent = custom3;
  return polyInOut2;
}(exponent);

// node_modules/d3-ease/src/sin.js
var pi = Math.PI;
var halfPi = pi / 2;
function sinIn(t) {
  return +t === 1 ? 1 : 1 - Math.cos(t * halfPi);
}
function sinOut(t) {
  return Math.sin(t * halfPi);
}
function sinInOut(t) {
  return (1 - Math.cos(pi * t)) / 2;
}

// node_modules/d3-ease/src/math.js
function tpmt(x2) {
  return (Math.pow(2, -10 * x2) - 9765625e-10) * 1.0009775171065494;
}

// node_modules/d3-ease/src/exp.js
function expIn(t) {
  return tpmt(1 - +t);
}
function expOut(t) {
  return 1 - tpmt(t);
}
function expInOut(t) {
  return ((t *= 2) <= 1 ? tpmt(1 - t) : 2 - tpmt(t - 1)) / 2;
}

// node_modules/d3-ease/src/circle.js
function circleIn(t) {
  return 1 - Math.sqrt(1 - t * t);
}
function circleOut(t) {
  return Math.sqrt(1 - --t * t);
}
function circleInOut(t) {
  return ((t *= 2) <= 1 ? 1 - Math.sqrt(1 - t * t) : Math.sqrt(1 - (t -= 2) * t) + 1) / 2;
}

// node_modules/d3-ease/src/bounce.js
var b1 = 4 / 11;
var b2 = 6 / 11;
var b3 = 8 / 11;
var b4 = 3 / 4;
var b5 = 9 / 11;
var b6 = 10 / 11;
var b7 = 15 / 16;
var b8 = 21 / 22;
var b9 = 63 / 64;
var b0 = 1 / b1 / b1;
function bounceIn(t) {
  return 1 - bounceOut(1 - t);
}
function bounceOut(t) {
  return (t = +t) < b1 ? b0 * t * t : t < b3 ? b0 * (t -= b2) * t + b4 : t < b6 ? b0 * (t -= b5) * t + b7 : b0 * (t -= b8) * t + b9;
}
function bounceInOut(t) {
  return ((t *= 2) <= 1 ? 1 - bounceOut(1 - t) : bounceOut(t - 1) + 1) / 2;
}

// node_modules/d3-ease/src/back.js
var overshoot = 1.70158;
var backIn = function custom4(s) {
  s = +s;
  function backIn2(t) {
    return (t = +t) * t * (s * (t - 1) + t);
  }
  backIn2.overshoot = custom4;
  return backIn2;
}(overshoot);
var backOut = function custom5(s) {
  s = +s;
  function backOut2(t) {
    return --t * t * ((t + 1) * s + t) + 1;
  }
  backOut2.overshoot = custom5;
  return backOut2;
}(overshoot);
var backInOut = function custom6(s) {
  s = +s;
  function backInOut2(t) {
    return ((t *= 2) < 1 ? t * t * ((s + 1) * t - s) : (t -= 2) * t * ((s + 1) * t + s) + 2) / 2;
  }
  backInOut2.overshoot = custom6;
  return backInOut2;
}(overshoot);

// node_modules/d3-ease/src/elastic.js
var tau = 2 * Math.PI;
var amplitude = 1;
var period = 0.3;
var elasticIn = function custom7(a, p) {
  var s = Math.asin(1 / (a = Math.max(1, a))) * (p /= tau);
  function elasticIn2(t) {
    return a * tpmt(- --t) * Math.sin((s - t) / p);
  }
  elasticIn2.amplitude = function(a2) {
    return custom7(a2, p * tau);
  };
  elasticIn2.period = function(p2) {
    return custom7(a, p2);
  };
  return elasticIn2;
}(amplitude, period);
var elasticOut = function custom8(a, p) {
  var s = Math.asin(1 / (a = Math.max(1, a))) * (p /= tau);
  function elasticOut2(t) {
    return 1 - a * tpmt(t = +t) * Math.sin((t + s) / p);
  }
  elasticOut2.amplitude = function(a2) {
    return custom8(a2, p * tau);
  };
  elasticOut2.period = function(p2) {
    return custom8(a, p2);
  };
  return elasticOut2;
}(amplitude, period);
var elasticInOut = function custom9(a, p) {
  var s = Math.asin(1 / (a = Math.max(1, a))) * (p /= tau);
  function elasticInOut2(t) {
    return ((t = t * 2 - 1) < 0 ? a * tpmt(-t) * Math.sin((s - t) / p) : 2 - a * tpmt(t) * Math.sin((s + t) / p)) / 2;
  }
  elasticInOut2.amplitude = function(a2) {
    return custom9(a2, p * tau);
  };
  elasticInOut2.period = function(p2) {
    return custom9(a, p2);
  };
  return elasticInOut2;
}(amplitude, period);

// node_modules/victory-core/es/victory-animation/util.js
var import_orderBy = __toESM(require_orderBy());
var import_isPlainObject = __toESM(require_isPlainObject());
var isInterpolatable = function(obj) {
  if (obj !== null) {
    switch (typeof obj) {
      case "undefined":
        return false;
      case "number":
        return !isNaN(obj) && obj !== Number.POSITIVE_INFINITY && obj !== Number.NEGATIVE_INFINITY;
      case "string":
        return true;
      case "boolean":
        return false;
      case "object":
        return obj instanceof Date || Array.isArray(obj) || (0, import_isPlainObject.default)(obj);
      case "function":
        return true;
    }
  }
  return false;
};
var interpolateImmediate = function(a, b, when) {
  if (when === void 0) {
    when = 0;
  }
  return function(t) {
    return t < when ? a : b;
  };
};
var interpolateFunction = function(a, b) {
  return function(t) {
    if (t >= 1) {
      return b;
    }
    return function() {
      const aval = typeof a === "function" ? a.apply(this, arguments) : a;
      const bval = typeof b === "function" ? b.apply(this, arguments) : b;
      return value_default(aval, bval)(t);
    };
  };
};
var interpolateObject = function(startValue, endValue) {
  const interpolateTypes = (x2, y2) => {
    if (x2 === y2 || !isInterpolatable(x2) || !isInterpolatable(y2)) {
      return interpolateImmediate(x2, y2);
    }
    if (typeof x2 === "function" || typeof y2 === "function") {
      return interpolateFunction(x2, y2);
    }
    if (typeof x2 === "object" && (0, import_isPlainObject.default)(x2) || typeof y2 === "object" && (0, import_isPlainObject.default)(y2)) {
      return interpolateObject(x2, y2);
    }
    return value_default(x2, y2);
  };
  const keyData = (val) => {
    return Array.isArray(val) ? (0, import_orderBy.default)(val, "key") : val;
  };
  const i = {};
  const c = {};
  let a = startValue;
  let b = endValue;
  let k;
  if (a === null || typeof a !== "object") {
    a = {};
  }
  if (b === null || typeof b !== "object") {
    b = {};
  }
  for (k in b) {
    if (k in a) {
      i[k] = interpolateTypes(keyData(a[k]), keyData(b[k]));
    } else {
      c[k] = b[k];
    }
  }
  return function(t) {
    for (k in i) {
      c[k] = i[k](t);
    }
    return c;
  };
};
var interpolateString = function(a, b) {
  const format2 = (val) => {
    return typeof val === "string" ? val.replace(/,/g, "") : val;
  };
  return value_default(format2(a), format2(b));
};
var victoryInterpolator = function(a, b) {
  if (a === b || !isInterpolatable(a) || !isInterpolatable(b)) {
    return interpolateImmediate(a, b);
  }
  if (typeof a === "function" || typeof b === "function") {
    return interpolateFunction(a, b);
  }
  if ((0, import_isPlainObject.default)(a) || (0, import_isPlainObject.default)(b)) {
    return interpolateObject(a, b);
  }
  if (typeof a === "string" || typeof b === "string") {
    return interpolateString(a, b);
  }
  return value_default(a, b);
};

// node_modules/victory-core/es/victory-util/timer-context.js
var import_react2 = __toESM(require_react());

// node_modules/victory-core/es/victory-util/timer.js
var Timer = class {
  constructor() {
    __publicField(this, "loop", () => {
      this.subscribers.forEach((s) => {
        s.callback(now() - s.startTime, s.duration);
      });
    });
    this.shouldAnimate = true;
    this.subscribers = [];
    this.timer = null;
    this.activeSubscriptions = 0;
  }
  bypassAnimation() {
    this.shouldAnimate = false;
  }
  resumeAnimation() {
    this.shouldAnimate = true;
  }
  start() {
    if (!this.timer) {
      this.timer = timer(this.loop);
    }
  }
  stop() {
    if (this.timer) {
      this.timer.stop();
      this.timer = null;
    }
  }
  subscribe(callback, duration) {
    const subscriptionID = this.subscribers.push({
      startTime: now(),
      callback,
      duration: this.shouldAnimate ? duration : 0
    });
    this.activeSubscriptions++;
    this.start();
    return subscriptionID;
  }
  unsubscribe(id) {
    if (id !== null && this.subscribers[id - 1]) {
      delete this.subscribers[id - 1];
      this.activeSubscriptions--;
    }
    if (this.activeSubscriptions === 0) {
      this.stop();
    }
  }
};

// node_modules/victory-core/es/victory-util/timer-context.js
var TimerContext = import_react2.default.createContext({
  transitionTimer: new Timer(),
  animationTimer: new Timer()
});
TimerContext.displayName = "TimerContext";
var timer_context_default = TimerContext;

// node_modules/victory-core/es/victory-animation/victory-animation.js
var formatAnimationName = (name) => {
  const capitalizedName = name.charAt(0).toUpperCase() + name.slice(1);
  return `ease${capitalizedName}`;
};
var DEFAULT_DURATION = 1e3;
var VictoryAnimation = (_ref) => {
  let {
    duration = DEFAULT_DURATION,
    easing = "quadInOut",
    delay = 0,
    data,
    children,
    onEnd
  } = _ref;
  const [state, setState] = import_react3.default.useState({
    data: Array.isArray(data) ? data[0] : data,
    animationInfo: {
      progress: 0,
      animating: false
    }
  });
  const timer2 = import_react3.default.useContext(timer_context_default).animationTimer;
  const queue = import_react3.default.useRef(Array.isArray(data) ? data.slice(1) : []);
  const interpolator = import_react3.default.useRef(null);
  const loopID = import_react3.default.useRef(void 0);
  const ease = d3_ease_exports[formatAnimationName(easing)];
  import_react3.default.useEffect(() => {
    if (queue.current.length) {
      traverseQueue();
    }
    return () => {
      if (loopID.current) {
        timer2.unsubscribe(loopID.current);
      } else {
        timer2.stop();
      }
    };
  }, []);
  import_react3.default.useEffect(() => {
    if (interpolator.current && state.animationInfo && state.animationInfo.progress < 1) {
      setState({
        data: interpolator.current(1),
        animationInfo: {
          progress: 1,
          animating: false,
          terminating: true
        }
      });
    } else {
      timer2.unsubscribe(loopID.current);
      queue.current = Array.isArray(data) ? data : [data];
      traverseQueue();
    }
  }, [data]);
  const traverseQueue = () => {
    if (queue.current.length) {
      const nextData = queue.current[0];
      interpolator.current = victoryInterpolator(state.data, nextData);
      if (delay) {
        setTimeout(() => {
          loopID.current = timer2.subscribe(functionToBeRunEachFrame, duration);
        }, delay);
      } else {
        loopID.current = timer2.subscribe(functionToBeRunEachFrame, duration);
      }
    } else if (onEnd) {
      onEnd();
    }
  };
  const functionToBeRunEachFrame = (elapsed) => {
    if (!interpolator.current) return;
    const step = duration ? elapsed / duration : 1;
    if (step >= 1) {
      setState({
        data: interpolator.current(1),
        animationInfo: {
          progress: 1,
          animating: false,
          terminating: true
        }
      });
      if (loopID.current) {
        timer2.unsubscribe(loopID.current);
      }
      queue.current.shift();
      traverseQueue();
      return;
    }
    setState({
      data: interpolator.current(ease(step)),
      animationInfo: {
        progress: step,
        animating: step < 1
      }
    });
  };
  return children(state.data, state.animationInfo);
};

// node_modules/victory-core/es/victory-container/victory-container.js
var import_uniqueId = __toESM(require_uniqueId());
var import_react17 = __toESM(require_react());

// node_modules/victory-core/es/victory-portal/portal.js
var import_react4 = __toESM(require_react());
function _extends() {
  _extends = Object.assign ? Object.assign.bind() : function(target) {
    for (var i = 1; i < arguments.length; i++) {
      var source = arguments[i];
      for (var key in source) {
        if (Object.prototype.hasOwnProperty.call(source, key)) {
          target[key] = source[key];
        }
      }
    }
    return target;
  };
  return _extends.apply(this, arguments);
}
var Portal = import_react4.default.forwardRef((props, ref) => {
  return import_react4.default.createElement("svg", _extends({
    ref
  }, props));
});

// node_modules/victory-core/es/victory-util/user-props.js
var user_props_exports = {};
__export(user_props_exports, {
  assert: () => assert,
  getSafeUserProps: () => getSafeUserProps,
  withSafeUserProps: () => withSafeUserProps
});
var React6 = __toESM(require_react());

// node_modules/victory-core/es/victory-util/helpers.js
var helpers_exports = {};
__export(helpers_exports, {
  createAccessor: () => createAccessor,
  degreesToRadians: () => degreesToRadians,
  evaluateProp: () => evaluateProp,
  evaluateStyle: () => evaluateStyle,
  getCurrentAxis: () => getCurrentAxis,
  getDefaultStyles: () => getDefaultStyles,
  getPadding: () => getPadding,
  getPoint: () => getPoint,
  getPolarOrigin: () => getPolarOrigin,
  getRadius: () => getRadius,
  getRange: () => getRange,
  getStyles: () => getStyles,
  invert: () => invert,
  isFunction: () => isFunction,
  isHorizontal: () => isHorizontal,
  isNil: () => isNil,
  isTooltip: () => isTooltip,
  mapValues: () => mapValues,
  modifyProps: () => modifyProps,
  omit: () => omit,
  radiansToDegrees: () => radiansToDegrees,
  range: () => range2,
  reduceChildren: () => reduceChildren,
  scalePoint: () => scalePoint
});
var import_pick = __toESM(require_pick());
var import_property = __toESM(require_property());
var import_defaults = __toESM(require_defaults());
var import_react5 = __toESM(require_react());
function getCartesianRange(props, axis) {
  const vertical = axis !== "x";
  const padding2 = getPadding(props);
  if (vertical) {
    return [props.height - padding2.bottom, padding2.top];
  }
  return [padding2.left, props.width - padding2.right];
}
function getPolarRange(props, axis) {
  if (axis === "x") {
    const startAngle = degreesToRadians(props.startAngle || 0);
    const endAngle = degreesToRadians(props.endAngle || 360);
    return [startAngle, endAngle];
  }
  return [props.innerRadius || 0, getRadius(props)];
}
function invert(original) {
  return Object.entries(original).reduce((acc, current) => {
    acc[current[1]] = current[0];
    return acc;
  }, {});
}
function omit(originalObject, ks) {
  if (ks === void 0) {
    ks = [];
  }
  const newObject = {};
  for (const key in originalObject) {
    if (ks.indexOf(key) >= 0) {
      continue;
    }
    if (!Object.prototype.hasOwnProperty.call(originalObject, key)) {
      continue;
    }
    newObject[key] = originalObject[key];
  }
  return newObject;
}
function getPoint(datum) {
  const exists2 = (val) => val !== void 0;
  const {
    _x,
    _x1,
    _x0,
    _voronoiX,
    _y,
    _y1,
    _y0,
    _voronoiY
  } = datum;
  const defaultX = exists2(_x1) ? _x1 : _x;
  const defaultY = exists2(_y1) ? _y1 : _y;
  const point3 = {
    x: exists2(_voronoiX) ? _voronoiX : defaultX,
    x0: exists2(_x0) ? _x0 : _x,
    y: exists2(_voronoiY) ? _voronoiY : defaultY,
    y0: exists2(_y0) ? _y0 : _y
  };
  return (0, import_defaults.default)({}, point3, datum);
}
function scalePoint(props, datum) {
  const {
    scale,
    polar,
    horizontal
  } = props;
  const d = getPoint(datum);
  const origin = props.origin || {
    x: 0,
    y: 0
  };
  const x2 = horizontal ? scale.y(d.y) : scale.x(d.x);
  const x0 = horizontal ? scale.y(d.y0) : scale.x(d.x0);
  const y2 = horizontal ? scale.x(d.x) : scale.y(d.y);
  const y0 = horizontal ? scale.x(d.x0) : scale.y(d.y0);
  return {
    x: polar ? y2 * Math.cos(x2) + origin.x : x2,
    x0: polar ? y0 * Math.cos(x0) + origin.x : x0,
    y: polar ? -y2 * Math.sin(x2) + origin.y : y2,
    y0: polar ? -y0 * Math.sin(x0) + origin.x : y0
  };
}
function getPadding(props, name) {
  if (name === void 0) {
    name = "padding";
  }
  const padding2 = props[name];
  const paddingVal = typeof padding2 === "number" ? padding2 : 0;
  const paddingObj = typeof padding2 === "object" ? padding2 : {};
  return {
    top: paddingObj.top || paddingVal,
    bottom: paddingObj.bottom || paddingVal,
    left: paddingObj.left || paddingVal,
    right: paddingObj.right || paddingVal
  };
}
function isTooltip(component) {
  const labelRole = component && component.type && component.type.role;
  return labelRole === "tooltip";
}
function getDefaultStyles(props, role) {
  const {
    theme = {},
    labelComponent
  } = props;
  const defaultStyles2 = theme[role] && theme[role].style || {};
  if (!isTooltip(labelComponent)) {
    return defaultStyles2;
  }
  const tooltipStyle = theme.tooltip && theme.tooltip.style || {};
  const labelStyle = (0, import_defaults.default)({}, tooltipStyle, defaultStyles2.labels);
  return (0, import_defaults.default)({}, {
    labels: labelStyle
  }, defaultStyles2);
}
function getStyles(style, defaultStyles2) {
  const width = "100%";
  const height = "100%";
  if (!style) {
    return (0, import_defaults.default)({
      parent: {
        height,
        width
      }
    }, defaultStyles2);
  }
  const {
    data,
    labels,
    parent
  } = style;
  const defaultParent = defaultStyles2 && defaultStyles2.parent || {};
  const defaultLabels = defaultStyles2 && defaultStyles2.labels || {};
  const defaultData6 = defaultStyles2 && defaultStyles2.data || {};
  return {
    parent: (0, import_defaults.default)({}, parent, defaultParent, {
      width,
      height
    }),
    labels: (0, import_defaults.default)({}, labels, defaultLabels),
    data: (0, import_defaults.default)({}, data, defaultData6)
  };
}
function evaluateProp(prop, props) {
  return isFunction(prop) ? prop(props) : prop;
}
function evaluateStyle(style, props) {
  if (props.disableInlineStyles) {
    return {};
  }
  if (!style || !Object.keys(style).some((value) => isFunction(style[value]))) {
    return style;
  }
  return Object.keys(style).reduce((prev, curr) => {
    prev[curr] = evaluateProp(style[curr], props);
    return prev;
  }, {});
}
function degreesToRadians(degrees) {
  return typeof degrees === "number" ? degrees * (Math.PI / 180) : degrees;
}
function radiansToDegrees(radians) {
  return typeof radians === "number" ? radians / (Math.PI / 180) : radians;
}
function getRadius(props) {
  const {
    left,
    right,
    top,
    bottom
  } = getPadding(props);
  const {
    width,
    height
  } = props;
  return Math.min(width - left - right, height - top - bottom) / 2;
}
function getPolarOrigin(props) {
  const {
    width,
    height
  } = props;
  const {
    top,
    bottom,
    left,
    right
  } = getPadding(props);
  const radius = Math.min(width - left - right, height - top - bottom) / 2;
  const offsetWidth = width / 2 + left - right;
  const offsetHeight = height / 2 + top - bottom;
  return {
    x: offsetWidth + radius > width ? radius + left - right : offsetWidth,
    y: offsetHeight + radius > height ? radius + top - bottom : offsetHeight
  };
}
function getRange(props, axis) {
  if (props.range && props.range[axis]) {
    return props.range[axis];
  } else if (props.range && Array.isArray(props.range)) {
    return props.range;
  }
  return props.polar ? getPolarRange(props, axis) : getCartesianRange(props, axis);
}
function isNil(value) {
  return value == null;
}
function isFunction(value) {
  return typeof value === "function";
}
function createAccessor(key) {
  if (isFunction(key)) {
    return key;
  } else if (key === null || key === void 0) {
    return (x2) => x2;
  }
  return (0, import_property.default)(key);
}
function modifyProps(props, fallbackProps22, role) {
  const theme = props.theme && props.theme[role] ? props.theme[role] : {};
  const themeProps = omit(theme, ["style"]);
  const horizontal = isHorizontal(props);
  const defaultObject = horizontal === void 0 ? {} : {
    horizontal
  };
  return (0, import_defaults.default)(defaultObject, props, themeProps, fallbackProps22);
}
function getCurrentAxis(axis, horizontal) {
  const otherAxis = axis === "x" ? "y" : "x";
  return horizontal ? otherAxis : axis;
}
function mapValues(values, fn) {
  if (values) {
    return Object.keys(values).reduce((acc, key) => {
      acc[key] = fn(values[key]);
      return acc;
    }, {});
  }
}
function range2(start, end, increment) {
  const startIndex = end ? start : 0;
  let endIndex = end ? end : start;
  if (!endIndex) endIndex = 0;
  const k = endIndex - startIndex;
  const length = Math.abs(k);
  const sign = k / length || 1;
  const inc = increment || 1;
  const arrayLength = Math.max(Math.ceil(length / inc), 0);
  return Array.from(Array(arrayLength), (_, i) => startIndex + i * sign * inc);
}
function reduceChildren(children, iteratee, parentProps, initialMemo, combine) {
  if (parentProps === void 0) {
    parentProps = {};
  }
  if (initialMemo === void 0) {
    initialMemo = [];
  }
  if (combine === void 0) {
    combine = (memo, item) => (
      // @ts-expect-error These defaults are hard to type
      memo.concat(item)
    );
  }
  const sharedProps = ["data", "domain", "categories", "polar", "startAngle", "endAngle", "minDomain", "maxDomain", "horizontal"];
  const traverseChildren = (childArray, names, parent) => {
    return childArray.reduce((memo, child, index) => {
      let newMemo = memo;
      const childRole = child.type && child.type.role;
      const childName = child.props.name || `${childRole}-${names[index]}`;
      if (child.props && child.props.children) {
        const childProps = Object.assign({}, child.props, (0, import_pick.default)(parentProps, sharedProps));
        const nestedChildren = child.type && child.type.role === "stack" && isFunction(child.type.getChildren) ? child.type.getChildren(childProps) : import_react5.default.Children.toArray(child.props.children).map((c) => {
          const nestedChildProps = Object.assign({}, c.props, (0, import_pick.default)(childProps, sharedProps));
          return import_react5.default.cloneElement(c, nestedChildProps);
        });
        const childNames2 = nestedChildren.map((c, i) => `${childName}-${i}`);
        const nestedResults = traverseChildren(nestedChildren, childNames2, child);
        newMemo = combine(newMemo, nestedResults);
      } else {
        const result = iteratee(child, childName, parent);
        if (result) {
          newMemo = combine(newMemo, result);
        }
      }
      return newMemo;
    }, initialMemo);
  };
  const validChildren = children.filter(import_react5.isValidElement);
  const childNames = validChildren.map((c, i) => i);
  return traverseChildren(validChildren, childNames);
}
function isHorizontal(props) {
  if (props.horizontal !== void 0 || !props.children) {
    return props.horizontal;
  }
  const traverseChildren = (childArray) => {
    return childArray.reduce((memo, child) => {
      const childProps = child.props || {};
      if (memo || childProps.horizontal || !childProps.children) {
        return memo || childProps.horizontal;
      }
      return traverseChildren(import_react5.default.Children.toArray(childProps.children));
    }, false);
  };
  return traverseChildren(import_react5.default.Children.toArray(props.children));
}

// node_modules/victory-core/es/victory-util/user-props.js
var USER_PROPS_SAFELIST = {
  startsWith: ["data-", "aria-"],
  exactMatch: []
};
var doesPropStartWith = (key) => {
  let startsWith = false;
  USER_PROPS_SAFELIST.startsWith.forEach((starterString) => {
    const regex = new RegExp(`\\b(${starterString})(\\w|-)+`, "g");
    if (regex.test(key)) startsWith = true;
  });
  return startsWith;
};
var isExactMatch = (key) => USER_PROPS_SAFELIST.exactMatch.includes(key);
var testIfSafeProp = (key) => {
  if (doesPropStartWith(key) || isExactMatch(key)) return true;
  return false;
};
function assert(value, message) {
  if (value === void 0 || value === null) {
    throw new Error(message);
  }
}
var getSafeUserProps = (props) => {
  const propsToFilter = {
    ...props
  };
  return Object.fromEntries(Object.entries(propsToFilter).filter((_ref) => {
    let [key] = _ref;
    return testIfSafeProp(key);
  }).map((_ref2) => {
    let [key, value] = _ref2;
    return [key, evaluateProp(value, props)];
  }));
};
var withSafeUserProps = (component, props) => {
  return React6.cloneElement(component, getSafeUserProps(props));
};

// node_modules/victory-core/es/victory-util/add-events.js
var import_pick3 = __toESM(require_pick());
var import_isEmpty2 = __toESM(require_isEmpty());
var import_defaults4 = __toESM(require_defaults());
var import_react8 = __toESM(require_react());
var import_react_fast_compare2 = __toESM(require_react_fast_compare());

// node_modules/victory-core/es/victory-transition/victory-transition.js
var import_pick2 = __toESM(require_pick());
var import_defaults3 = __toESM(require_defaults());
var import_react7 = __toESM(require_react());

// node_modules/victory-core/es/victory-util/collection.js
var collection_exports = {};
__export(collection_exports, {
  containsDates: () => containsDates,
  containsNumbers: () => containsNumbers,
  containsOnlyStrings: () => containsOnlyStrings,
  containsStrings: () => containsStrings,
  difference: () => difference,
  getMaxValue: () => getMaxValue,
  getMinValue: () => getMinValue,
  isArrayOfArrays: () => isArrayOfArrays,
  removeUndefined: () => removeUndefined
});
function isNonEmptyArray(collection) {
  return Array.isArray(collection) && collection.length > 0;
}
function containsStrings(collection) {
  return Array.isArray(collection) && collection.some((value) => typeof value === "string");
}
function containsDates(collection) {
  return Array.isArray(collection) && collection.some((value) => value instanceof Date);
}
function containsNumbers(collection) {
  return Array.isArray(collection) && collection.some((value) => typeof value === "number");
}
function containsOnlyStrings(collection) {
  return isNonEmptyArray(collection) && collection.every((value) => typeof value === "string");
}
function difference(a, b) {
  if (a && b) {
    return a.filter((value) => !b.includes(value));
  }
  return [];
}
function isArrayOfArrays(collection) {
  return isNonEmptyArray(collection) && collection.every(Array.isArray);
}
function removeUndefined(arr) {
  return arr.filter((el) => el !== void 0);
}
function getMaxValue(arr) {
  for (var _len = arguments.length, values = new Array(_len > 1 ? _len - 1 : 0), _key = 1; _key < _len; _key++) {
    values[_key - 1] = arguments[_key];
  }
  const array = arr.concat(values);
  return containsDates(array) ? new Date(Math.max(...array)) : Math.max(...array);
}
function getMinValue(arr) {
  for (var _len2 = arguments.length, values = new Array(_len2 > 1 ? _len2 - 1 : 0), _key2 = 1; _key2 < _len2; _key2++) {
    values[_key2 - 1] = arguments[_key2];
  }
  const array = arr.concat(values);
  return containsDates(array) ? new Date(Math.min(...array)) : Math.min(...array);
}

// node_modules/victory-core/es/victory-util/transitions.js
var transitions_exports = {};
__export(transitions_exports, {
  getInitialTransitionState: () => getInitialTransitionState,
  getTransitionPropsFactory: () => getTransitionPropsFactory
});
var import_identity = __toESM(require_identity());
var import_defaults2 = __toESM(require_defaults());
var import_react6 = __toESM(require_react());
function getDatumKey(datum, idx) {
  return (datum.key || idx).toString();
}
function getKeyedData(data) {
  return data.reduce((keyedData, datum, idx) => {
    const key = getDatumKey(datum, idx);
    keyedData[key] = datum;
    return keyedData;
  }, {});
}
function getKeyedDataDifference(a, b) {
  let hasDifference = false;
  const difference2 = Object.keys(a).reduce((_difference, key) => {
    if (!(key in b)) {
      hasDifference = true;
      _difference[key] = true;
    }
    return _difference;
  }, {});
  return hasDifference && difference2;
}
function getNodeTransitions(oldData, nextData) {
  const oldDataKeyed = oldData && getKeyedData(oldData);
  const nextDataKeyed = nextData && getKeyedData(nextData);
  return {
    entering: oldDataKeyed && getKeyedDataDifference(nextDataKeyed, oldDataKeyed),
    exiting: nextDataKeyed && getKeyedDataDifference(oldDataKeyed, nextDataKeyed)
  };
}
function getChildData(child) {
  if (child.type && child.type.getData) {
    return child.type.getData(child.props);
  }
  return child.props && child.props.data || false;
}
function getInitialTransitionState(oldChildren, nextChildren) {
  let nodesWillExit = false;
  let nodesWillEnter = false;
  const getTransition = (oldChild, newChild) => {
    if (!newChild || oldChild.type !== newChild.type) {
      return {};
    }
    const {
      entering,
      exiting
    } = getNodeTransitions(getChildData(oldChild), getChildData(newChild)) || {};
    nodesWillExit = nodesWillExit || !!exiting;
    nodesWillEnter = nodesWillEnter || !!entering;
    return {
      entering: entering || false,
      exiting: exiting || false
    };
  };
  const getTransitionsFromChildren = (old, next) => {
    return old.map((child, idx) => {
      if (child && child.props && child.props.children && next[idx]) {
        return getTransitionsFromChildren(import_react6.default.Children.toArray(old[idx].props.children), import_react6.default.Children.toArray(next[idx].props.children));
      }
      return getTransition(child, next[idx]);
    });
  };
  const childrenTransitions = getTransitionsFromChildren(import_react6.default.Children.toArray(oldChildren), import_react6.default.Children.toArray(nextChildren));
  return {
    nodesWillExit,
    nodesWillEnter,
    childrenTransitions,
    // TODO: This may need to be refactored for the following situation.
    //       The component receives new props, and the data provided
    //       is a perfect match for the previous data and domain except
    //       for new nodes. In this case, we wouldn't want a delay before
    //       the new nodes appear.
    nodesShouldEnter: false
  };
}
function getInitialChildProps(animate, data) {
  const after = animate.onEnter && animate.onEnter.after ? animate.onEnter.after : import_identity.default;
  return {
    data: data.map((datum, idx) => Object.assign({}, datum, after(datum, idx, data)))
  };
}
function getChildBeforeLoad(animate, child, data, cb) {
  const newAnimate = Object.assign({}, animate, {
    onEnd: cb
  });
  if (newAnimate && newAnimate.onLoad && !newAnimate.onLoad.duration) {
    return {
      animate: newAnimate,
      data
    };
  }
  const before = newAnimate.onLoad && newAnimate.onLoad.before ? newAnimate.onLoad.before : import_identity.default;
  const newData = data.map((datum, idx) => {
    return Object.assign({}, datum, before(datum, idx, data));
  });
  return {
    animate: newAnimate,
    data: newData,
    clipWidth: 0
  };
}
function getChildOnLoad(animate, data, cb) {
  const newAnimate = Object.assign({}, animate, {
    onEnd: cb
  });
  let newData = data;
  if (newAnimate && newAnimate.onLoad && !newAnimate.onLoad.duration) {
    return {
      animate,
      data
    };
  }
  const after = animate.onLoad && animate.onLoad.after ? animate.onLoad.after : import_identity.default;
  newData = data.map((datum, idx) => {
    return Object.assign({}, datum, after(datum, idx, data));
  });
  return {
    animate: newAnimate,
    data: newData
  };
}
function getChildPropsOnExit(animate, child, data, exitingNodes, cb) {
  const onExit = animate && animate.onExit;
  const newAnimate = Object.assign({}, animate, onExit);
  let newData = data;
  if (exitingNodes) {
    animate.onEnd = cb;
    const before = animate.onExit && animate.onExit.before ? animate.onExit.before : import_identity.default;
    newData = data.map((datum, idx) => {
      const key = (datum.key || idx).toString();
      return exitingNodes[key] ? Object.assign({}, datum, before(datum, idx, data)) : datum;
    });
  }
  return {
    animate: newAnimate,
    data: newData
  };
}
function getChildPropsBeforeEnter(animate, child, data, enteringNodes, cb) {
  let newAnimate = animate;
  let newData = data;
  if (enteringNodes) {
    newAnimate = Object.assign({}, animate, {
      onEnd: cb
    });
    const before = animate.onEnter && animate.onEnter.before ? animate.onEnter.before : import_identity.default;
    newData = data.map((datum, idx) => {
      const key = (datum.key || idx).toString();
      return enteringNodes[key] ? Object.assign({}, datum, before(datum, idx, data)) : datum;
    });
  }
  return {
    animate: newAnimate,
    data: newData
  };
}
function getChildPropsOnEnter(animate, data, enteringNodes, cb) {
  const onEnter = animate && animate.onEnter;
  const newAnimate = Object.assign({}, animate, onEnter);
  let newData = data;
  if (enteringNodes) {
    newAnimate.onEnd = cb;
    const after = newAnimate.onEnter && newAnimate.onEnter.after ? newAnimate.onEnter.after : import_identity.default;
    newData = data.map((datum, idx) => {
      const key = getDatumKey(datum, idx);
      return enteringNodes[key] ? Object.assign({}, datum, after(datum, idx, data)) : datum;
    });
  }
  return {
    animate: newAnimate,
    data: newData
  };
}
function getTransitionPropsFactory(props, state, setState) {
  const nodesWillExit = state && state.nodesWillExit;
  const nodesWillEnter = state && state.nodesWillEnter;
  const nodesShouldEnter = state && state.nodesShouldEnter;
  const nodesShouldLoad = state && state.nodesShouldLoad;
  const nodesDoneLoad = state && state.nodesDoneLoad;
  const childrenTransitions = state && state.childrenTransitions || [];
  const transitionDurations = {
    enter: props.animate && props.animate.onEnter && props.animate.onEnter.duration,
    exit: props.animate && props.animate.onExit && props.animate.onExit.duration,
    load: props.animate && props.animate.onLoad && props.animate.onLoad.duration,
    move: props.animate && props.animate.duration
  };
  const onLoad = (child, data, animate) => {
    if (nodesShouldLoad) {
      return getChildOnLoad(animate, data, () => {
        setState({
          nodesShouldLoad: false,
          nodesDoneLoad: true
        });
      });
    }
    return getChildBeforeLoad(animate, child, data, () => {
      setState({
        nodesDoneLoad: true
      });
    });
  };
  const onExit = (nodes, child, data, animate) => {
    return getChildPropsOnExit(animate, child, data, nodes, () => {
      setState({
        nodesWillExit: false
      });
    });
  };
  const onEnter = (nodes, child, data, animate) => {
    if (nodesShouldEnter) {
      return getChildPropsOnEnter(animate, data, nodes, () => {
        setState({
          nodesWillEnter: false
        });
      });
    }
    return getChildPropsBeforeEnter(animate, child, data, nodes, () => {
      setState({
        nodesShouldEnter: true
      });
    });
  };
  const getChildTransitionDuration = function(child, type) {
    const animate = child.props.animate;
    if (!child.type) {
      return {};
    }
    const defaultTransitions = child.props && child.props.polar ? child.type.defaultPolarTransitions || child.type.defaultTransitions : child.type.defaultTransitions;
    if (defaultTransitions) {
      const animationDuration = animate[type] && animate[type].duration;
      return animationDuration !== void 0 ? animationDuration : defaultTransitions[type] && defaultTransitions[type].duration;
    }
    return {};
  };
  return function getTransitionProps(child, index) {
    const data = getChildData(child) || [];
    const animate = (0, import_defaults2.default)({}, props.animate, child.props.animate);
    const defaultTransitions = child.props.polar ? child.type.defaultPolarTransitions || child.type.defaultTransitions : child.type.defaultTransitions;
    animate.onExit = (0, import_defaults2.default)({}, animate.onExit, defaultTransitions && defaultTransitions.onExit);
    animate.onEnter = (0, import_defaults2.default)({}, animate.onEnter, defaultTransitions && defaultTransitions.onEnter);
    animate.onLoad = (0, import_defaults2.default)({}, animate.onLoad, defaultTransitions && defaultTransitions.onLoad);
    const childTransitions = childrenTransitions[index] || childrenTransitions[0];
    if (!nodesDoneLoad) {
      const load = transitionDurations.load !== void 0 ? transitionDurations.load : getChildTransitionDuration(child, "onLoad");
      const animation = {
        duration: load
      };
      return onLoad(child, data, Object.assign({}, animate, animation));
    } else if (nodesWillExit) {
      const exitingNodes = childTransitions && childTransitions.exiting;
      const exit = transitionDurations.exit !== void 0 ? transitionDurations.exit : getChildTransitionDuration(child, "onExit");
      const animation = exitingNodes ? {
        duration: exit
      } : {
        delay: exit
      };
      return onExit(exitingNodes, child, data, Object.assign({}, animate, animation));
    } else if (nodesWillEnter) {
      const enteringNodes = childTransitions && childTransitions.entering;
      const enter = transitionDurations.enter !== void 0 ? transitionDurations.enter : getChildTransitionDuration(child, "onEnter");
      const move = transitionDurations.move !== void 0 ? transitionDurations.move : child.props.animate && child.props.animate.duration;
      const animation = {
        duration: nodesShouldEnter && enteringNodes ? enter : move
      };
      return onEnter(enteringNodes, child, data, Object.assign({}, animate, animation));
    } else if (!state && animate && animate.onExit) {
      return getInitialChildProps(animate, data);
    }
    return {
      animate,
      data
    };
  };
}

// node_modules/victory-core/es/victory-transition/victory-transition.js
var import_react_fast_compare = __toESM(require_react_fast_compare());
function _extends2() {
  _extends2 = Object.assign ? Object.assign.bind() : function(target) {
    for (var i = 1; i < arguments.length; i++) {
      var source = arguments[i];
      for (var key in source) {
        if (Object.prototype.hasOwnProperty.call(source, key)) {
          target[key] = source[key];
        }
      }
    }
    return target;
  };
  return _extends2.apply(this, arguments);
}
var VictoryTransition = class extends import_react7.default.Component {
  constructor(props, context) {
    super(props, context);
    this.state = {
      nodesShouldLoad: false,
      nodesDoneLoad: false
    };
    const child = this.props.children;
    const polar = child.props.polar;
    this.continuous = !polar && child.type && child.type.continuous === true;
    this.timer = this.context.transitionTimer;
  }
  componentDidMount() {
    this.setState({
      nodesShouldLoad: true
    });
  }
  shouldComponentUpdate(nextProps) {
    if (!(0, import_react_fast_compare.default)(this.props, nextProps)) {
      this.timer.bypassAnimation();
      this.setState(this.getTransitionState(this.props, nextProps), () => this.timer.resumeAnimation());
    }
    return true;
  }
  componentWillUnmount() {
    this.timer.stop();
  }
  getTransitionState(props, nextProps) {
    const {
      animate
    } = props;
    if (!animate) {
      return {};
    } else if (animate.parentState) {
      const state = animate.parentState;
      const oldProps = state.nodesWillExit ? props : null;
      return {
        oldProps,
        nextProps
      };
    }
    const oldChildren = import_react7.default.Children.toArray(props.children);
    const nextChildren = import_react7.default.Children.toArray(nextProps.children);
    const {
      nodesWillExit,
      nodesWillEnter,
      childrenTransitions,
      nodesShouldEnter
    } = getInitialTransitionState(oldChildren, nextChildren);
    return {
      nodesWillExit,
      nodesWillEnter,
      childrenTransitions,
      nodesShouldEnter,
      oldProps: nodesWillExit ? props : null,
      nextProps
    };
  }
  getDomainFromChildren(props, axis) {
    const getChildDomains = (children) => {
      return children.reduce((memo, child2) => {
        if (child2.type && isFunction(child2.type.getDomain)) {
          const childDomain = child2.props && child2.type.getDomain(child2.props, axis);
          return childDomain ? memo.concat(childDomain) : memo;
        } else if (child2.props && child2.props.children) {
          return memo.concat(getChildDomains(import_react7.default.Children.toArray(child2.props.children)));
        }
        return memo;
      }, []);
    };
    const child = import_react7.default.Children.toArray(props.children)[0];
    const childProps = child.props || {};
    const domain = Array.isArray(childProps.domain) ? childProps.domain : childProps.domain && childProps.domain[axis];
    if (!childProps.children && domain) {
      return domain;
    }
    const childDomains = getChildDomains([child]);
    return childDomains.length === 0 ? [0, 1] : [getMinValue(childDomains), getMaxValue(childDomains)];
  }
  pickProps() {
    if (!this.state) {
      return this.props;
    }
    return this.state.nodesWillExit ? this.state.oldProps || this.props : this.props;
  }
  pickDomainProps(props) {
    var _a;
    const parentState = (_a = props.animate) == null ? void 0 : _a.parentState;
    if (parentState && parentState.nodesWillExit) {
      return this.continuous || parentState.continuous ? parentState.nextProps || this.state.nextProps || props : props;
    }
    return this.continuous && this.state.nodesWillExit ? this.state.nextProps || props : props;
  }
  getClipWidth(props, child) {
    const getDefaultClipWidth = () => {
      const range3 = getRange(child.props, "x");
      return range3 ? Math.abs(range3[1] - range3[0]) : props.width;
    };
    const clipWidth = this.transitionProps ? this.transitionProps.clipWidth : void 0;
    return clipWidth !== void 0 ? clipWidth : getDefaultClipWidth();
  }
  render() {
    var _a;
    const props = this.pickProps();
    const getTransitionProps = ((_a = this.props.animate) == null ? void 0 : _a.getTransitions) ? this.props.animate.getTransitions : getTransitionPropsFactory(props, this.state, (newState) => this.setState(newState));
    const child = import_react7.default.Children.toArray(props.children)[0];
    const transitionProps = getTransitionProps(child);
    this.transitionProps = transitionProps;
    const domain = {
      x: this.getDomainFromChildren(this.pickDomainProps(props), "x"),
      y: this.getDomainFromChildren(props, "y")
    };
    const clipWidth = this.getClipWidth(props, child);
    const combinedProps = (0, import_defaults3.default)({
      domain,
      clipWidth
    }, transitionProps, child.props);
    const animationWhitelist = props.animationWhitelist || [];
    const whitelist = animationWhitelist.concat(["clipWidth"]);
    const propsToAnimate = whitelist.length ? (0, import_pick2.default)(combinedProps, whitelist) : combinedProps;
    return import_react7.default.createElement(VictoryAnimation, _extends2({}, combinedProps.animate, {
      data: propsToAnimate
    }), (newProps) => {
      if (child.props.groupComponent) {
        const groupComponent = this.continuous ? import_react7.default.cloneElement(child.props.groupComponent, {
          clipWidth: newProps.clipWidth || 0
        }) : child.props.groupComponent;
        return import_react7.default.cloneElement(child, (0, import_defaults3.default)({
          animate: null,
          animating: true,
          groupComponent
        }, newProps, combinedProps));
      }
      return import_react7.default.cloneElement(child, (0, import_defaults3.default)({
        animate: null,
        animating: true
      }, newProps, combinedProps));
    });
  }
};
__publicField(VictoryTransition, "displayName", "VictoryTransition");
__publicField(VictoryTransition, "contextType", timer_context_default);

// node_modules/victory-core/es/victory-util/events.js
var events_exports = {};
__export(events_exports, {
  emulateReactEvent: () => emulateReactEvent,
  getComponentEvents: () => getComponentEvents,
  getEventState: () => getEventState,
  getEvents: () => getEvents,
  getExternalMutation: () => getExternalMutation,
  getExternalMutations: () => getExternalMutations,
  getExternalMutationsWithChildren: () => getExternalMutationsWithChildren,
  getGlobalEventNameFromKey: () => getGlobalEventNameFromKey,
  getGlobalEvents: () => getGlobalEvents,
  getPartialEvents: () => getPartialEvents,
  getScopedEvents: () => getScopedEvents,
  omitGlobalEvents: () => omitGlobalEvents
});
var import_uniq = __toESM(require_uniq());
var import_omitBy = __toESM(require_omitBy());
var import_pickBy = __toESM(require_pickBy());
var import_isEmpty = __toESM(require_isEmpty());
var GLOBAL_EVENT_REGEX = /^onGlobal(.*)$/;
function getEvents(props, target, eventKey, getScopedEvents2) {
  const getEventsByTarget = (events) => {
    const getSelectedEvents = () => {
      const targetEvents = events.reduce((memo, event) => {
        if (event.target !== void 0) {
          const matchesTarget = Array.isArray(event.target) ? event.target.includes(target) : `${event.target}` === `${target}`;
          return matchesTarget ? memo.concat(event) : memo;
        }
        return memo.concat(event);
      }, []);
      if (eventKey !== void 0 && target !== "parent") {
        return targetEvents.filter((obj) => {
          const targetKeys = obj.eventKey;
          const useKey = (key) => key ? `${key}` === `${eventKey}` : true;
          return Array.isArray(targetKeys) ? targetKeys.some((k) => useKey(k)) : useKey(targetKeys);
        });
      }
      return targetEvents;
    };
    const selectedEvents = getSelectedEvents();
    return Array.isArray(selectedEvents) && selectedEvents.reduce((memo, event) => {
      return event ? Object.assign(memo, event.eventHandlers) : memo;
    }, {});
  };
  const getAllEvents2 = () => {
    if (Array.isArray(this.componentEvents)) {
      return Array.isArray(props.events) ? this.componentEvents.concat(...props.events) : this.componentEvents;
    }
    return props.events;
  };
  const allEvents = getAllEvents2();
  const ownEvents = allEvents && isFunction(getScopedEvents2) ? getScopedEvents2(getEventsByTarget(allEvents), target) : void 0;
  if (!props.sharedEvents) {
    return ownEvents;
  }
  const getSharedEvents = props.sharedEvents.getEvents;
  const sharedEvents = props.sharedEvents.events && getSharedEvents(getEventsByTarget(props.sharedEvents.events), target);
  return Object.assign({}, sharedEvents, ownEvents);
}
function getScopedEvents(events, namespace, childType, baseProps3) {
  if ((0, import_isEmpty.default)(events)) {
    return {};
  }
  const newBaseProps = baseProps3 || this.baseProps;
  const getTargetProps = (identifier, type) => {
    const {
      childName,
      target,
      key
    } = identifier;
    const baseType = type === "props" ? newBaseProps : this.state || {};
    const base = childName === void 0 || childName === null || !baseType[childName] ? baseType : baseType[childName];
    return key === "parent" ? base.parent : base[key] && base[key][target];
  };
  const parseEvent = (eventReturn, eventKey) => {
    const childNames = namespace === "parent" ? eventReturn.childName : eventReturn.childName || childType;
    const target = eventReturn.target || namespace;
    const getKeys = (childName) => {
      if (target === "parent") {
        return "parent";
      }
      if (eventReturn.eventKey === "all") {
        return newBaseProps[childName] ? Object.keys(newBaseProps[childName]).filter((value) => value !== "parent") : Object.keys(newBaseProps).filter((value) => value !== "parent");
      } else if (eventReturn.eventKey === void 0 && eventKey === "parent") {
        return newBaseProps[childName] ? Object.keys(newBaseProps[childName]) : Object.keys(newBaseProps);
      }
      return eventReturn.eventKey !== void 0 ? eventReturn.eventKey : eventKey;
    };
    const getMutationObject = (key, childName) => {
      const baseState = this.state || {};
      if (!isFunction(eventReturn.mutation)) {
        return baseState;
      }
      const mutationTargetProps = getTargetProps({
        childName,
        key,
        target
      }, "props");
      const mutationTargetState = getTargetProps({
        childName,
        key,
        target
      }, "state");
      const mutatedProps = eventReturn.mutation(Object.assign({}, mutationTargetProps, mutationTargetState), newBaseProps);
      const childState = baseState[childName] || {};
      const filterState = (state) => {
        if (state[key] && state[key][target]) {
          delete state[key][target];
        }
        if (state[key] && !Object.keys(state[key]).length) {
          delete state[key];
        }
        return state;
      };
      const extendState = (state) => {
        return target === "parent" ? Object.assign(state, {
          [key]: Object.assign(state[key] || {}, mutatedProps)
        }) : Object.assign(state, {
          [key]: Object.assign(state[key] || {}, {
            [target]: mutatedProps
          })
        });
      };
      const updateState = (state) => {
        return mutatedProps ? extendState(state) : filterState(state);
      };
      return childName !== void 0 && childName !== null ? Object.assign(baseState, {
        [childName]: updateState(childState)
      }) : updateState(baseState);
    };
    const getReturnByChild = (childName) => {
      const mutationKeys = getKeys(childName);
      return Array.isArray(mutationKeys) ? mutationKeys.reduce((memo, key) => {
        return Object.assign(memo, getMutationObject(key, childName));
      }, {}) : getMutationObject(mutationKeys, childName);
    };
    const allChildNames = childNames === "all" ? Object.keys(newBaseProps).filter((value) => value !== "parent") : childNames;
    return Array.isArray(allChildNames) ? allChildNames.reduce((memo, childName) => {
      return Object.assign(memo, getReturnByChild(childName));
    }, {}) : getReturnByChild(allChildNames);
  };
  const parseEventReturn = (eventReturn, eventKey) => {
    return Array.isArray(eventReturn) ? eventReturn.reduce((memo, props) => Object.assign({}, memo, parseEvent(props, eventKey)), {}) : parseEvent(eventReturn, eventKey);
  };
  const compileCallbacks = (eventReturn) => {
    const getCallback = (obj) => isFunction(obj.callback) && obj.callback;
    const callbacks = Array.isArray(eventReturn) ? eventReturn.map((evtObj) => getCallback(evtObj)) : [getCallback(eventReturn)];
    const callbackArray = callbacks.filter((callback) => callback !== false);
    return callbackArray.length ? () => callbackArray.forEach((callback) => callback()) : void 0;
  };
  const onEvent = (evt, childProps, eventKey, eventName) => {
    const eventReturn = events[eventName](evt, childProps, eventKey, this);
    if (!(0, import_isEmpty.default)(eventReturn)) {
      const callbacks = compileCallbacks(eventReturn);
      this.setState(parseEventReturn(eventReturn, eventKey), callbacks);
    }
  };
  return Object.keys(events).reduce((memo, event) => {
    memo[event] = onEvent;
    return memo;
  }, {});
}
function getPartialEvents(events, eventKey, childProps) {
  if (!events) return {};
  return Object.keys(events).reduce((memo, eventName) => {
    const appliedEvent = (evt) => events[eventName](evt, childProps, eventKey, eventName);
    memo[eventName] = appliedEvent;
    return memo;
  }, {});
}
function getEventState(eventKey, namespace, childType) {
  const state = this.state || {};
  if (!childType) {
    return eventKey === "parent" ? state[eventKey] && state[eventKey][namespace] || state[eventKey] : state[eventKey] && state[eventKey][namespace];
  }
  return state[childType] && state[childType][eventKey] && state[childType][eventKey][namespace];
}
function getExternalMutationsWithChildren(mutations, baseProps3, baseState, childNames) {
  if (baseProps3 === void 0) {
    baseProps3 = {};
  }
  if (baseState === void 0) {
    baseState = {};
  }
  return childNames.reduce((memo, childName) => {
    const childState = baseState[childName];
    const mutation = getExternalMutations(mutations, baseProps3[childName], baseState[childName], childName);
    memo[childName] = mutation ? mutation : childState;
    return (0, import_pickBy.default)(memo, (v) => !(0, import_isEmpty.default)(v));
  }, {});
}
function getExternalMutations(mutations, baseProps3, baseState, childName) {
  if (baseProps3 === void 0) {
    baseProps3 = {};
  }
  if (baseState === void 0) {
    baseState = {};
  }
  const eventKeys = Object.keys(baseProps3);
  return eventKeys.reduce((memo, eventKey) => {
    const keyState = baseState[eventKey] || {};
    const keyProps = baseProps3[eventKey] || {};
    if (eventKey === "parent") {
      const identifier = {
        eventKey,
        target: "parent"
      };
      const mutation = getExternalMutation(mutations, keyProps, keyState, identifier);
      memo[eventKey] = mutation !== void 0 ? Object.assign({}, keyState, mutation) : keyState;
    } else {
      const targets = (0, import_uniq.default)(Object.keys(keyProps).concat(Object.keys(keyState)));
      memo[eventKey] = targets.reduce((m, target) => {
        const identifier = {
          eventKey,
          target,
          childName
        };
        const mutation = getExternalMutation(mutations, keyProps[target], keyState[target], identifier);
        m[target] = mutation !== void 0 ? Object.assign({}, keyState[target], mutation) : keyState[target];
        return (0, import_pickBy.default)(m, (v) => !(0, import_isEmpty.default)(v));
      }, {});
    }
    return (0, import_pickBy.default)(memo, (v) => !(0, import_isEmpty.default)(v));
  }, {});
}
function getExternalMutation(mutations, baseProps3, baseState, identifier) {
  const filterMutations = (mutation, type) => {
    if (typeof mutation[type] === "string") {
      return mutation[type] === "all" || mutation[type] === identifier[type];
    } else if (Array.isArray(mutation[type])) {
      const stringArray = mutation[type].map((m) => `${m}`);
      return stringArray.includes(identifier[type]);
    }
    return false;
  };
  let scopedMutations = Array.isArray(mutations) ? mutations : [mutations];
  if (identifier.childName) {
    scopedMutations = mutations.filter((m) => filterMutations(m, "childName"));
  }
  const targetMutations = scopedMutations.filter((m) => filterMutations(m, "target"));
  if ((0, import_isEmpty.default)(targetMutations)) {
    return void 0;
  }
  const keyMutations = targetMutations.filter((m) => filterMutations(m, "eventKey"));
  if ((0, import_isEmpty.default)(keyMutations)) {
    return void 0;
  }
  return keyMutations.reduce((memo, curr) => {
    const mutationFunction = curr && isFunction(curr.mutation) ? curr.mutation : () => void 0;
    const currentMutation = mutationFunction(Object.assign({}, baseProps3, baseState));
    return Object.assign({}, memo, currentMutation);
  }, {});
}
function getComponentEvents(props, components) {
  const events = Array.isArray(components) && components.reduce((memo, componentName) => {
    const component = props[componentName];
    const defaultEvents = component && component.type && component.type.defaultEvents;
    const componentEvents = isFunction(defaultEvents) ? defaultEvents(component.props) : defaultEvents;
    return Array.isArray(componentEvents) ? memo.concat(...componentEvents) : memo;
  }, []);
  return events && events.length ? events : void 0;
}
function getGlobalEventNameFromKey(key) {
  const match = key.match(GLOBAL_EVENT_REGEX);
  return match && match[1] && match[1].toLowerCase();
}
var getGlobalEvents = (events) => (0, import_pickBy.default)(events, (_, key) => GLOBAL_EVENT_REGEX.test(key));
var omitGlobalEvents = (events) => (0, import_omitBy.default)(events, (_, key) => GLOBAL_EVENT_REGEX.test(key));
var emulateReactEvent = (event) => Object.assign(event, {
  nativeEvent: event
});

// node_modules/victory-core/es/victory-util/add-events.js
var datumHasXandY = (datum) => {
  return !isNil(datum._x) && !isNil(datum._y);
};
var defaultComponents = [{
  name: "parent",
  index: "parent"
}, {
  name: "data"
}, {
  name: "labels"
}];
function addEvents(WrappedComponent, options7) {
  if (options7 === void 0) {
    options7 = {};
  }
  class AddEventsMixin extends WrappedComponent {
    constructor(props) {
      super(props);
      __publicField(this, "state", {});
      __publicField(this, "getEventState", getEventState.bind(this));
      __publicField(this, "getScopedEvents", getScopedEvents.bind(this));
      __publicField(this, "getEvents", (p, target, eventKey) => {
        return getEvents.call(this, p, target, eventKey, this.getScopedEvents);
      });
      __publicField(this, "externalMutations", this.getExternalMutations(this.props));
      __publicField(this, "calculatedState", this.getStateChanges(this.props));
      __publicField(this, "globalEvents", {});
      __publicField(this, "prevGlobalEventKeys", []);
      __publicField(this, "boundGlobalEvents", {});
      this.cacheValues(this.getCalculatedValues(props));
    }
    shouldComponentUpdate(nextProps) {
      const externalMutations = this.getExternalMutations(nextProps);
      const animating = this.props.animating || this.props.animate;
      const newMutation = !(0, import_react_fast_compare2.default)(externalMutations, this.externalMutations);
      if (animating || newMutation) {
        this.cacheValues(this.getCalculatedValues(nextProps));
        this.externalMutations = externalMutations;
        this.applyExternalMutations(nextProps, externalMutations);
        return true;
      }
      const calculatedState = this.getStateChanges(nextProps);
      if (!(0, import_react_fast_compare2.default)(this.calculatedState, calculatedState)) {
        this.cacheValues(this.getCalculatedValues(nextProps));
        return true;
      }
      if (!(0, import_react_fast_compare2.default)(this.props, nextProps)) {
        this.cacheValues(this.getCalculatedValues(nextProps));
        return true;
      }
      return false;
    }
    componentDidMount() {
      const globalEventKeys = Object.keys(this.globalEvents);
      globalEventKeys.forEach((key) => this.addGlobalListener(key));
      this.prevGlobalEventKeys = globalEventKeys;
    }
    componentDidUpdate(prevProps) {
      const calculatedState = this.getStateChanges(prevProps);
      this.calculatedState = calculatedState;
      const globalEventKeys = Object.keys(this.globalEvents);
      const removedGlobalEventKeys = difference(this.prevGlobalEventKeys, globalEventKeys);
      removedGlobalEventKeys.forEach((key) => this.removeGlobalListener(key));
      const addedGlobalEventKeys = difference(globalEventKeys, this.prevGlobalEventKeys);
      addedGlobalEventKeys.forEach((key) => this.addGlobalListener(key));
      this.prevGlobalEventKeys = globalEventKeys;
    }
    componentWillUnmount() {
      this.prevGlobalEventKeys.forEach((key) => this.removeGlobalListener(key));
    }
    addGlobalListener(key) {
      const boundListener = (event) => {
        const listener = this.globalEvents[key];
        return listener && listener(emulateReactEvent(event));
      };
      this.boundGlobalEvents[key] = boundListener;
      window.addEventListener(getGlobalEventNameFromKey(key), boundListener);
    }
    removeGlobalListener(key) {
      window.removeEventListener(getGlobalEventNameFromKey(key), this.boundGlobalEvents[key]);
    }
    // compile all state changes from own and parent state. Order doesn't matter, as any state
    // state change should trigger a re-render
    getStateChanges(props) {
      if (!this.hasEvents) {
        return {};
      }
      const getState = (key, type) => {
        const result = (0, import_defaults4.default)({}, this.getEventState(key, type), this.getSharedEventState(key, type));
        return (0, import_isEmpty2.default)(result) ? void 0 : result;
      };
      const components = options7.components || defaultComponents;
      const stateChanges = components.map((component) => {
        if (!props.standalone && component.name === "parent") {
          return void 0;
        }
        return component.index !== void 0 ? getState(component.index, component.name) : this.dataKeys.map((key) => getState(key, component.name)).filter(Boolean);
      }).filter(Boolean);
      return stateChanges;
    }
    applyExternalMutations(props, externalMutations) {
      if (!(0, import_isEmpty2.default)(externalMutations)) {
        const callbacks = props.externalEventMutations.reduce((memo, mutation) => isFunction(mutation.callback) ? memo.concat(mutation.callback) : memo, []);
        const compiledCallbacks = callbacks.length ? () => {
          callbacks.forEach((c) => c());
        } : void 0;
        this.setState(externalMutations, compiledCallbacks);
      }
    }
    getCalculatedValues(props) {
      const {
        sharedEvents
      } = props;
      const components = WrappedComponent.expectedComponents;
      const componentEvents = getComponentEvents(props, components);
      const getSharedEventState = sharedEvents && isFunction(sharedEvents.getEventState) ? sharedEvents.getEventState : () => void 0;
      const baseProps3 = this.getBaseProps(props, getSharedEventState);
      const dataKeys = Object.keys(baseProps3).filter((key) => key !== "parent");
      const hasEvents = props.events || props.sharedEvents || componentEvents;
      const events = this.getAllEvents(props);
      return {
        componentEvents,
        getSharedEventState,
        baseProps: baseProps3,
        dataKeys,
        hasEvents,
        events
      };
    }
    getExternalMutations(props) {
      const {
        sharedEvents,
        externalEventMutations
      } = props;
      return (0, import_isEmpty2.default)(externalEventMutations) || sharedEvents ? void 0 : getExternalMutations(externalEventMutations, this.baseProps, this.state);
    }
    cacheValues(obj) {
      Object.keys(obj).forEach((key) => {
        this[key] = obj[key];
      });
    }
    getBaseProps(props, getSharedEventState) {
      const getSharedEventStateFunction = getSharedEventState || this.getSharedEventState.bind(this);
      const sharedParentState = getSharedEventStateFunction("parent", "parent");
      const parentState = this.getEventState("parent", "parent");
      const baseParentProps = (0, import_defaults4.default)({}, parentState, sharedParentState);
      const parentPropsList = baseParentProps.parentControlledProps;
      const parentProps = parentPropsList ? (0, import_pick3.default)(baseParentProps, parentPropsList) : {};
      const modifiedProps = (0, import_defaults4.default)({}, parentProps, props);
      return typeof WrappedComponent.getBaseProps === "function" ? WrappedComponent.getBaseProps(modifiedProps) : {};
    }
    getAllEvents(props) {
      if (Array.isArray(this.componentEvents)) {
        return Array.isArray(props.events) ? this.componentEvents.concat(...props.events) : this.componentEvents;
      }
      return props.events;
    }
    getComponentProps(component, type, index) {
      const name = this.props.name || WrappedComponent.role;
      const key = this.dataKeys && this.dataKeys[index] || index;
      const id = `${name}-${type}-${key}`;
      const baseProps3 = this.baseProps[key] && this.baseProps[key][type] || this.baseProps[key];
      if (!baseProps3 && !this.hasEvents) {
        return void 0;
      }
      const currentProps = component && typeof component === "object" && "props" in component ? component.props : void 0;
      if (this.hasEvents) {
        const baseEvents = this.getEvents(this.props, type, key);
        const componentProps = (0, import_defaults4.default)({
          index,
          key: id
        }, this.getEventState(key, type), this.getSharedEventState(key, type), currentProps, baseProps3, {
          id
        });
        const events = (0, import_defaults4.default)({}, getPartialEvents(baseEvents, key, componentProps), componentProps.events);
        return Object.assign({}, componentProps, {
          events
        });
      }
      return (0, import_defaults4.default)({
        index,
        key: id
      }, currentProps, baseProps3, {
        id
      });
    }
    renderContainer(component, children) {
      const isContainer = component.type && component.type.role === "container";
      const parentProps = isContainer ? this.getComponentProps(component, "parent", "parent") : {};
      if (parentProps.events) {
        this.globalEvents = getGlobalEvents(parentProps.events);
        parentProps.events = omitGlobalEvents(parentProps.events);
      }
      return import_react8.default.cloneElement(component, parentProps, children);
    }
    animateComponent(props, defaultAnimationWhitelist) {
      var _a;
      const animationWhitelist = typeof props.animate === "object" && ((_a = props.animate) == null ? void 0 : _a.animationWhitelist) || defaultAnimationWhitelist;
      const Comp = this.constructor;
      return import_react8.default.createElement(VictoryTransition, {
        animate: props.animate,
        animationWhitelist
      }, import_react8.default.createElement(Comp, props));
    }
    // Used by `VictoryLine` and `VictoryArea`
    renderContinuousData(props) {
      const {
        dataComponent,
        labelComponent,
        groupComponent
      } = props;
      const dataKeys = this.dataKeys.filter((value) => value !== "all");
      const labelComponents = dataKeys.reduce((memo, key) => {
        let newMemo = memo;
        const labelProps = this.getComponentProps(labelComponent, "labels", key);
        if (labelProps && labelProps.text !== void 0 && labelProps.text !== null) {
          newMemo = newMemo.concat(import_react8.default.cloneElement(labelComponent, labelProps));
        }
        return newMemo;
      }, []);
      const dataProps = this.getComponentProps(dataComponent, "data", "all");
      const children = [import_react8.default.cloneElement(dataComponent, dataProps), ...labelComponents];
      return this.renderContainer(groupComponent, children);
    }
    renderData(props, shouldRenderDatum) {
      if (shouldRenderDatum === void 0) {
        shouldRenderDatum = datumHasXandY;
      }
      const {
        dataComponent,
        labelComponent,
        groupComponent
      } = props;
      const dataComponents = this.dataKeys.reduce((validDataComponents, _dataKey, index) => {
        const dataProps = this.getComponentProps(dataComponent, "data", index);
        if (shouldRenderDatum(dataProps.datum)) {
          validDataComponents.push(import_react8.default.cloneElement(dataComponent, dataProps));
        }
        return validDataComponents;
      }, []);
      const labelComponents = this.dataKeys.map((_dataKey, index) => {
        const labelProps = this.getComponentProps(labelComponent, "labels", index);
        if (labelProps.text !== void 0 && labelProps.text !== null) {
          return import_react8.default.cloneElement(labelComponent, labelProps);
        }
        return void 0;
      }).filter(Boolean);
      const children = [...dataComponents, ...labelComponents];
      return this.renderContainer(groupComponent, children);
    }
  }
  return AddEventsMixin;
}

// node_modules/victory-core/es/victory-util/merge-refs.js
function mergeRefs(refs) {
  return (value) => {
    refs.forEach((ref) => {
      if (isFunction(ref)) {
        ref(value);
      } else if (ref !== null && ref !== void 0) {
        ref.current = value;
      }
    });
  };
}

// node_modules/victory-core/es/victory-util/axis.js
var axis_exports = {};
__export(axis_exports, {
  findAxisComponents: () => findAxisComponents,
  getAxis: () => getAxis,
  getAxisComponent: () => getAxisComponent,
  getAxisComponentsWithParent: () => getAxisComponentsWithParent,
  getAxisValue: () => getAxisValue,
  getDomain: () => getDomain2,
  getOrigin: () => getOrigin,
  getOriginSign: () => getOriginSign,
  getTickFormat: () => getTickFormat,
  getTicks: () => getTicks,
  isVertical: () => isVertical,
  modifyProps: () => modifyProps2,
  stringTicks: () => stringTicks
});
var import_orderBy3 = __toESM(require_orderBy());
var import_uniq3 = __toESM(require_uniq());
var import_isObject = __toESM(require_isObject());
var import_defaults5 = __toESM(require_defaults());
var import_react11 = __toESM(require_react());

// node_modules/victory-core/es/victory-util/domain.js
var domain_exports = {};
__export(domain_exports, {
  createDomainFunction: () => createDomainFunction,
  formatDomain: () => formatDomain,
  getDomain: () => getDomain,
  getDomainFromCategories: () => getDomainFromCategories,
  getDomainFromData: () => getDomainFromData,
  getDomainFromMinMax: () => getDomainFromMinMax,
  getDomainFromProps: () => getDomainFromProps,
  getDomainWithZero: () => getDomainWithZero,
  getMaxFromProps: () => getMaxFromProps,
  getMinFromProps: () => getMinFromProps,
  getSymmetricDomain: () => getSymmetricDomain,
  isDomainComponent: () => isDomainComponent
});
var import_isDate = __toESM(require_isDate());
var import_sortedUniq = __toESM(require_sortedUniq());
var import_isPlainObject4 = __toESM(require_isPlainObject());
var import_react10 = __toESM(require_react());

// node_modules/victory-core/es/victory-util/data.js
var data_exports = {};
__export(data_exports, {
  createStringMap: () => createStringMap,
  downsample: () => downsample,
  formatData: () => formatData,
  formatDataFromDomain: () => formatDataFromDomain,
  generateData: () => generateData,
  getCategories: () => getCategories,
  getData: () => getData,
  getStringsFromAxes: () => getStringsFromAxes,
  getStringsFromCategories: () => getStringsFromCategories,
  getStringsFromData: () => getStringsFromData,
  isDataComponent: () => isDataComponent
});
var import_omitBy2 = __toESM(require_omitBy());
var import_isUndefined = __toESM(require_isUndefined());
var import_isEqual = __toESM(require_isEqual());
var import_isEmpty3 = __toESM(require_isEmpty());
var import_orderBy2 = __toESM(require_orderBy());
var import_property2 = __toESM(require_property());
var import_isPlainObject3 = __toESM(require_isPlainObject());
var import_uniq2 = __toESM(require_uniq());
var import_react9 = __toESM(require_react());

// node_modules/victory-core/es/victory-util/scale.js
var scale_exports = {};
__export(scale_exports, {
  getBaseScale: () => getBaseScale,
  getDefaultScale: () => getDefaultScale,
  getScaleFromName: () => getScaleFromName,
  getScaleFromProps: () => getScaleFromProps,
  getScaleType: () => getScaleType,
  getType: () => getType,
  validScale: () => validScale
});
var import_isPlainObject2 = __toESM(require_isPlainObject());

// node_modules/victory-core/node_modules/victory-vendor/es/d3-scale.js
var d3_scale_exports = {};
__export(d3_scale_exports, {
  scaleBand: () => band,
  scaleDiverging: () => diverging,
  scaleDivergingLog: () => divergingLog,
  scaleDivergingPow: () => divergingPow,
  scaleDivergingSqrt: () => divergingSqrt,
  scaleDivergingSymlog: () => divergingSymlog,
  scaleIdentity: () => identity2,
  scaleImplicit: () => implicit,
  scaleLinear: () => linear2,
  scaleLog: () => log,
  scaleOrdinal: () => ordinal,
  scalePoint: () => point,
  scalePow: () => pow,
  scaleQuantile: () => quantile2,
  scaleQuantize: () => quantize,
  scaleRadial: () => radial,
  scaleSequential: () => sequential,
  scaleSequentialLog: () => sequentialLog,
  scaleSequentialPow: () => sequentialPow,
  scaleSequentialQuantile: () => sequentialQuantile,
  scaleSequentialSqrt: () => sequentialSqrt,
  scaleSequentialSymlog: () => sequentialSymlog,
  scaleSqrt: () => sqrt,
  scaleSymlog: () => symlog,
  scaleThreshold: () => threshold,
  scaleTime: () => time,
  scaleUtc: () => utcTime,
  tickFormat: () => tickFormat
});

// node_modules/d3-scale/src/init.js
function initRange(domain, range3) {
  switch (arguments.length) {
    case 0:
      break;
    case 1:
      this.range(domain);
      break;
    default:
      this.range(range3).domain(domain);
      break;
  }
  return this;
}
function initInterpolator(domain, interpolator) {
  switch (arguments.length) {
    case 0:
      break;
    case 1: {
      if (typeof domain === "function") this.interpolator(domain);
      else this.range(domain);
      break;
    }
    default: {
      this.domain(domain);
      if (typeof interpolator === "function") this.interpolator(interpolator);
      else this.range(interpolator);
      break;
    }
  }
  return this;
}

// node_modules/d3-scale/src/ordinal.js
var implicit = Symbol("implicit");
function ordinal() {
  var index = new InternMap(), domain = [], range3 = [], unknown = implicit;
  function scale(d) {
    let i = index.get(d);
    if (i === void 0) {
      if (unknown !== implicit) return unknown;
      index.set(d, i = domain.push(d) - 1);
    }
    return range3[i % range3.length];
  }
  scale.domain = function(_) {
    if (!arguments.length) return domain.slice();
    domain = [], index = new InternMap();
    for (const value of _) {
      if (index.has(value)) continue;
      index.set(value, domain.push(value) - 1);
    }
    return scale;
  };
  scale.range = function(_) {
    return arguments.length ? (range3 = Array.from(_), scale) : range3.slice();
  };
  scale.unknown = function(_) {
    return arguments.length ? (unknown = _, scale) : unknown;
  };
  scale.copy = function() {
    return ordinal(domain, range3).unknown(unknown);
  };
  initRange.apply(scale, arguments);
  return scale;
}

// node_modules/d3-scale/src/band.js
function band() {
  var scale = ordinal().unknown(void 0), domain = scale.domain, ordinalRange = scale.range, r0 = 0, r1 = 1, step, bandwidth, round = false, paddingInner = 0, paddingOuter = 0, align = 0.5;
  delete scale.unknown;
  function rescale() {
    var n = domain().length, reverse = r1 < r0, start = reverse ? r1 : r0, stop = reverse ? r0 : r1;
    step = (stop - start) / Math.max(1, n - paddingInner + paddingOuter * 2);
    if (round) step = Math.floor(step);
    start += (stop - start - step * (n - paddingInner)) * align;
    bandwidth = step * (1 - paddingInner);
    if (round) start = Math.round(start), bandwidth = Math.round(bandwidth);
    var values = range(n).map(function(i) {
      return start + step * i;
    });
    return ordinalRange(reverse ? values.reverse() : values);
  }
  scale.domain = function(_) {
    return arguments.length ? (domain(_), rescale()) : domain();
  };
  scale.range = function(_) {
    return arguments.length ? ([r0, r1] = _, r0 = +r0, r1 = +r1, rescale()) : [r0, r1];
  };
  scale.rangeRound = function(_) {
    return [r0, r1] = _, r0 = +r0, r1 = +r1, round = true, rescale();
  };
  scale.bandwidth = function() {
    return bandwidth;
  };
  scale.step = function() {
    return step;
  };
  scale.round = function(_) {
    return arguments.length ? (round = !!_, rescale()) : round;
  };
  scale.padding = function(_) {
    return arguments.length ? (paddingInner = Math.min(1, paddingOuter = +_), rescale()) : paddingInner;
  };
  scale.paddingInner = function(_) {
    return arguments.length ? (paddingInner = Math.min(1, _), rescale()) : paddingInner;
  };
  scale.paddingOuter = function(_) {
    return arguments.length ? (paddingOuter = +_, rescale()) : paddingOuter;
  };
  scale.align = function(_) {
    return arguments.length ? (align = Math.max(0, Math.min(1, _)), rescale()) : align;
  };
  scale.copy = function() {
    return band(domain(), [r0, r1]).round(round).paddingInner(paddingInner).paddingOuter(paddingOuter).align(align);
  };
  return initRange.apply(rescale(), arguments);
}
function pointish(scale) {
  var copy3 = scale.copy;
  scale.padding = scale.paddingOuter;
  delete scale.paddingInner;
  delete scale.paddingOuter;
  scale.copy = function() {
    return pointish(copy3());
  };
  return scale;
}
function point() {
  return pointish(band.apply(null, arguments).paddingInner(1));
}

// node_modules/d3-scale/src/constant.js
function constants(x2) {
  return function() {
    return x2;
  };
}

// node_modules/d3-scale/src/number.js
function number(x2) {
  return +x2;
}

// node_modules/d3-scale/src/continuous.js
var unit = [0, 1];
function identity(x2) {
  return x2;
}
function normalize(a, b) {
  return (b -= a = +a) ? function(x2) {
    return (x2 - a) / b;
  } : constants(isNaN(b) ? NaN : 0.5);
}
function clamper(a, b) {
  var t;
  if (a > b) t = a, a = b, b = t;
  return function(x2) {
    return Math.max(a, Math.min(b, x2));
  };
}
function bimap(domain, range3, interpolate) {
  var d0 = domain[0], d1 = domain[1], r0 = range3[0], r1 = range3[1];
  if (d1 < d0) d0 = normalize(d1, d0), r0 = interpolate(r1, r0);
  else d0 = normalize(d0, d1), r0 = interpolate(r0, r1);
  return function(x2) {
    return r0(d0(x2));
  };
}
function polymap(domain, range3, interpolate) {
  var j = Math.min(domain.length, range3.length) - 1, d = new Array(j), r = new Array(j), i = -1;
  if (domain[j] < domain[0]) {
    domain = domain.slice().reverse();
    range3 = range3.slice().reverse();
  }
  while (++i < j) {
    d[i] = normalize(domain[i], domain[i + 1]);
    r[i] = interpolate(range3[i], range3[i + 1]);
  }
  return function(x2) {
    var i2 = bisect_default(domain, x2, 1, j) - 1;
    return r[i2](d[i2](x2));
  };
}
function copy(source, target) {
  return target.domain(source.domain()).range(source.range()).interpolate(source.interpolate()).clamp(source.clamp()).unknown(source.unknown());
}
function transformer() {
  var domain = unit, range3 = unit, interpolate = value_default, transform, untransform, unknown, clamp = identity, piecewise2, output, input;
  function rescale() {
    var n = Math.min(domain.length, range3.length);
    if (clamp !== identity) clamp = clamper(domain[0], domain[n - 1]);
    piecewise2 = n > 2 ? polymap : bimap;
    output = input = null;
    return scale;
  }
  function scale(x2) {
    return x2 == null || isNaN(x2 = +x2) ? unknown : (output || (output = piecewise2(domain.map(transform), range3, interpolate)))(transform(clamp(x2)));
  }
  scale.invert = function(y2) {
    return clamp(untransform((input || (input = piecewise2(range3, domain.map(transform), number_default)))(y2)));
  };
  scale.domain = function(_) {
    return arguments.length ? (domain = Array.from(_, number), rescale()) : domain.slice();
  };
  scale.range = function(_) {
    return arguments.length ? (range3 = Array.from(_), rescale()) : range3.slice();
  };
  scale.rangeRound = function(_) {
    return range3 = Array.from(_), interpolate = round_default, rescale();
  };
  scale.clamp = function(_) {
    return arguments.length ? (clamp = _ ? true : identity, rescale()) : clamp !== identity;
  };
  scale.interpolate = function(_) {
    return arguments.length ? (interpolate = _, rescale()) : interpolate;
  };
  scale.unknown = function(_) {
    return arguments.length ? (unknown = _, scale) : unknown;
  };
  return function(t, u) {
    transform = t, untransform = u;
    return rescale();
  };
}
function continuous() {
  return transformer()(identity, identity);
}

// node_modules/d3-scale/src/tickFormat.js
function tickFormat(start, stop, count, specifier) {
  var step = tickStep(start, stop, count), precision;
  specifier = formatSpecifier(specifier == null ? ",f" : specifier);
  switch (specifier.type) {
    case "s": {
      var value = Math.max(Math.abs(start), Math.abs(stop));
      if (specifier.precision == null && !isNaN(precision = precisionPrefix_default(step, value))) specifier.precision = precision;
      return formatPrefix(specifier, value);
    }
    case "":
    case "e":
    case "g":
    case "p":
    case "r": {
      if (specifier.precision == null && !isNaN(precision = precisionRound_default(step, Math.max(Math.abs(start), Math.abs(stop))))) specifier.precision = precision - (specifier.type === "e");
      break;
    }
    case "f":
    case "%": {
      if (specifier.precision == null && !isNaN(precision = precisionFixed_default(step))) specifier.precision = precision - (specifier.type === "%") * 2;
      break;
    }
  }
  return format(specifier);
}

// node_modules/d3-scale/src/linear.js
function linearish(scale) {
  var domain = scale.domain;
  scale.ticks = function(count) {
    var d = domain();
    return ticks(d[0], d[d.length - 1], count == null ? 10 : count);
  };
  scale.tickFormat = function(count, specifier) {
    var d = domain();
    return tickFormat(d[0], d[d.length - 1], count == null ? 10 : count, specifier);
  };
  scale.nice = function(count) {
    if (count == null) count = 10;
    var d = domain();
    var i0 = 0;
    var i1 = d.length - 1;
    var start = d[i0];
    var stop = d[i1];
    var prestep;
    var step;
    var maxIter = 10;
    if (stop < start) {
      step = start, start = stop, stop = step;
      step = i0, i0 = i1, i1 = step;
    }
    while (maxIter-- > 0) {
      step = tickIncrement(start, stop, count);
      if (step === prestep) {
        d[i0] = start;
        d[i1] = stop;
        return domain(d);
      } else if (step > 0) {
        start = Math.floor(start / step) * step;
        stop = Math.ceil(stop / step) * step;
      } else if (step < 0) {
        start = Math.ceil(start * step) / step;
        stop = Math.floor(stop * step) / step;
      } else {
        break;
      }
      prestep = step;
    }
    return scale;
  };
  return scale;
}
function linear2() {
  var scale = continuous();
  scale.copy = function() {
    return copy(scale, linear2());
  };
  initRange.apply(scale, arguments);
  return linearish(scale);
}

// node_modules/d3-scale/src/identity.js
function identity2(domain) {
  var unknown;
  function scale(x2) {
    return x2 == null || isNaN(x2 = +x2) ? unknown : x2;
  }
  scale.invert = scale;
  scale.domain = scale.range = function(_) {
    return arguments.length ? (domain = Array.from(_, number), scale) : domain.slice();
  };
  scale.unknown = function(_) {
    return arguments.length ? (unknown = _, scale) : unknown;
  };
  scale.copy = function() {
    return identity2(domain).unknown(unknown);
  };
  domain = arguments.length ? Array.from(domain, number) : [0, 1];
  return linearish(scale);
}

// node_modules/d3-scale/src/nice.js
function nice(domain, interval) {
  domain = domain.slice();
  var i0 = 0, i1 = domain.length - 1, x0 = domain[i0], x1 = domain[i1], t;
  if (x1 < x0) {
    t = i0, i0 = i1, i1 = t;
    t = x0, x0 = x1, x1 = t;
  }
  domain[i0] = interval.floor(x0);
  domain[i1] = interval.ceil(x1);
  return domain;
}

// node_modules/d3-scale/src/log.js
function transformLog(x2) {
  return Math.log(x2);
}
function transformExp(x2) {
  return Math.exp(x2);
}
function transformLogn(x2) {
  return -Math.log(-x2);
}
function transformExpn(x2) {
  return -Math.exp(-x2);
}
function pow10(x2) {
  return isFinite(x2) ? +("1e" + x2) : x2 < 0 ? 0 : x2;
}
function powp(base) {
  return base === 10 ? pow10 : base === Math.E ? Math.exp : (x2) => Math.pow(base, x2);
}
function logp(base) {
  return base === Math.E ? Math.log : base === 10 && Math.log10 || base === 2 && Math.log2 || (base = Math.log(base), (x2) => Math.log(x2) / base);
}
function reflect(f) {
  return (x2, k) => -f(-x2, k);
}
function loggish(transform) {
  const scale = transform(transformLog, transformExp);
  const domain = scale.domain;
  let base = 10;
  let logs;
  let pows;
  function rescale() {
    logs = logp(base), pows = powp(base);
    if (domain()[0] < 0) {
      logs = reflect(logs), pows = reflect(pows);
      transform(transformLogn, transformExpn);
    } else {
      transform(transformLog, transformExp);
    }
    return scale;
  }
  scale.base = function(_) {
    return arguments.length ? (base = +_, rescale()) : base;
  };
  scale.domain = function(_) {
    return arguments.length ? (domain(_), rescale()) : domain();
  };
  scale.ticks = (count) => {
    const d = domain();
    let u = d[0];
    let v = d[d.length - 1];
    const r = v < u;
    if (r) [u, v] = [v, u];
    let i = logs(u);
    let j = logs(v);
    let k;
    let t;
    const n = count == null ? 10 : +count;
    let z = [];
    if (!(base % 1) && j - i < n) {
      i = Math.floor(i), j = Math.ceil(j);
      if (u > 0) for (; i <= j; ++i) {
        for (k = 1; k < base; ++k) {
          t = i < 0 ? k / pows(-i) : k * pows(i);
          if (t < u) continue;
          if (t > v) break;
          z.push(t);
        }
      }
      else for (; i <= j; ++i) {
        for (k = base - 1; k >= 1; --k) {
          t = i > 0 ? k / pows(-i) : k * pows(i);
          if (t < u) continue;
          if (t > v) break;
          z.push(t);
        }
      }
      if (z.length * 2 < n) z = ticks(u, v, n);
    } else {
      z = ticks(i, j, Math.min(j - i, n)).map(pows);
    }
    return r ? z.reverse() : z;
  };
  scale.tickFormat = (count, specifier) => {
    if (count == null) count = 10;
    if (specifier == null) specifier = base === 10 ? "s" : ",";
    if (typeof specifier !== "function") {
      if (!(base % 1) && (specifier = formatSpecifier(specifier)).precision == null) specifier.trim = true;
      specifier = format(specifier);
    }
    if (count === Infinity) return specifier;
    const k = Math.max(1, base * count / scale.ticks().length);
    return (d) => {
      let i = d / pows(Math.round(logs(d)));
      if (i * base < base - 0.5) i *= base;
      return i <= k ? specifier(d) : "";
    };
  };
  scale.nice = () => {
    return domain(nice(domain(), {
      floor: (x2) => pows(Math.floor(logs(x2))),
      ceil: (x2) => pows(Math.ceil(logs(x2)))
    }));
  };
  return scale;
}
function log() {
  const scale = loggish(transformer()).domain([1, 10]);
  scale.copy = () => copy(scale, log()).base(scale.base());
  initRange.apply(scale, arguments);
  return scale;
}

// node_modules/d3-scale/src/symlog.js
function transformSymlog(c) {
  return function(x2) {
    return Math.sign(x2) * Math.log1p(Math.abs(x2 / c));
  };
}
function transformSymexp(c) {
  return function(x2) {
    return Math.sign(x2) * Math.expm1(Math.abs(x2)) * c;
  };
}
function symlogish(transform) {
  var c = 1, scale = transform(transformSymlog(c), transformSymexp(c));
  scale.constant = function(_) {
    return arguments.length ? transform(transformSymlog(c = +_), transformSymexp(c)) : c;
  };
  return linearish(scale);
}
function symlog() {
  var scale = symlogish(transformer());
  scale.copy = function() {
    return copy(scale, symlog()).constant(scale.constant());
  };
  return initRange.apply(scale, arguments);
}

// node_modules/d3-scale/src/pow.js
function transformPow(exponent2) {
  return function(x2) {
    return x2 < 0 ? -Math.pow(-x2, exponent2) : Math.pow(x2, exponent2);
  };
}
function transformSqrt(x2) {
  return x2 < 0 ? -Math.sqrt(-x2) : Math.sqrt(x2);
}
function transformSquare(x2) {
  return x2 < 0 ? -x2 * x2 : x2 * x2;
}
function powish(transform) {
  var scale = transform(identity, identity), exponent2 = 1;
  function rescale() {
    return exponent2 === 1 ? transform(identity, identity) : exponent2 === 0.5 ? transform(transformSqrt, transformSquare) : transform(transformPow(exponent2), transformPow(1 / exponent2));
  }
  scale.exponent = function(_) {
    return arguments.length ? (exponent2 = +_, rescale()) : exponent2;
  };
  return linearish(scale);
}
function pow() {
  var scale = powish(transformer());
  scale.copy = function() {
    return copy(scale, pow()).exponent(scale.exponent());
  };
  initRange.apply(scale, arguments);
  return scale;
}
function sqrt() {
  return pow.apply(null, arguments).exponent(0.5);
}

// node_modules/d3-scale/src/radial.js
function square(x2) {
  return Math.sign(x2) * x2 * x2;
}
function unsquare(x2) {
  return Math.sign(x2) * Math.sqrt(Math.abs(x2));
}
function radial() {
  var squared = continuous(), range3 = [0, 1], round = false, unknown;
  function scale(x2) {
    var y2 = unsquare(squared(x2));
    return isNaN(y2) ? unknown : round ? Math.round(y2) : y2;
  }
  scale.invert = function(y2) {
    return squared.invert(square(y2));
  };
  scale.domain = function(_) {
    return arguments.length ? (squared.domain(_), scale) : squared.domain();
  };
  scale.range = function(_) {
    return arguments.length ? (squared.range((range3 = Array.from(_, number)).map(square)), scale) : range3.slice();
  };
  scale.rangeRound = function(_) {
    return scale.range(_).round(true);
  };
  scale.round = function(_) {
    return arguments.length ? (round = !!_, scale) : round;
  };
  scale.clamp = function(_) {
    return arguments.length ? (squared.clamp(_), scale) : squared.clamp();
  };
  scale.unknown = function(_) {
    return arguments.length ? (unknown = _, scale) : unknown;
  };
  scale.copy = function() {
    return radial(squared.domain(), range3).round(round).clamp(squared.clamp()).unknown(unknown);
  };
  initRange.apply(scale, arguments);
  return linearish(scale);
}

// node_modules/d3-scale/src/quantile.js
function quantile2() {
  var domain = [], range3 = [], thresholds = [], unknown;
  function rescale() {
    var i = 0, n = Math.max(1, range3.length);
    thresholds = new Array(n - 1);
    while (++i < n) thresholds[i - 1] = quantileSorted(domain, i / n);
    return scale;
  }
  function scale(x2) {
    return x2 == null || isNaN(x2 = +x2) ? unknown : range3[bisect_default(thresholds, x2)];
  }
  scale.invertExtent = function(y2) {
    var i = range3.indexOf(y2);
    return i < 0 ? [NaN, NaN] : [
      i > 0 ? thresholds[i - 1] : domain[0],
      i < thresholds.length ? thresholds[i] : domain[domain.length - 1]
    ];
  };
  scale.domain = function(_) {
    if (!arguments.length) return domain.slice();
    domain = [];
    for (let d of _) if (d != null && !isNaN(d = +d)) domain.push(d);
    domain.sort(ascending);
    return rescale();
  };
  scale.range = function(_) {
    return arguments.length ? (range3 = Array.from(_), rescale()) : range3.slice();
  };
  scale.unknown = function(_) {
    return arguments.length ? (unknown = _, scale) : unknown;
  };
  scale.quantiles = function() {
    return thresholds.slice();
  };
  scale.copy = function() {
    return quantile2().domain(domain).range(range3).unknown(unknown);
  };
  return initRange.apply(scale, arguments);
}

// node_modules/d3-scale/src/quantize.js
function quantize() {
  var x0 = 0, x1 = 1, n = 1, domain = [0.5], range3 = [0, 1], unknown;
  function scale(x2) {
    return x2 != null && x2 <= x2 ? range3[bisect_default(domain, x2, 0, n)] : unknown;
  }
  function rescale() {
    var i = -1;
    domain = new Array(n);
    while (++i < n) domain[i] = ((i + 1) * x1 - (i - n) * x0) / (n + 1);
    return scale;
  }
  scale.domain = function(_) {
    return arguments.length ? ([x0, x1] = _, x0 = +x0, x1 = +x1, rescale()) : [x0, x1];
  };
  scale.range = function(_) {
    return arguments.length ? (n = (range3 = Array.from(_)).length - 1, rescale()) : range3.slice();
  };
  scale.invertExtent = function(y2) {
    var i = range3.indexOf(y2);
    return i < 0 ? [NaN, NaN] : i < 1 ? [x0, domain[0]] : i >= n ? [domain[n - 1], x1] : [domain[i - 1], domain[i]];
  };
  scale.unknown = function(_) {
    return arguments.length ? (unknown = _, scale) : scale;
  };
  scale.thresholds = function() {
    return domain.slice();
  };
  scale.copy = function() {
    return quantize().domain([x0, x1]).range(range3).unknown(unknown);
  };
  return initRange.apply(linearish(scale), arguments);
}

// node_modules/d3-scale/src/threshold.js
function threshold() {
  var domain = [0.5], range3 = [0, 1], unknown, n = 1;
  function scale(x2) {
    return x2 != null && x2 <= x2 ? range3[bisect_default(domain, x2, 0, n)] : unknown;
  }
  scale.domain = function(_) {
    return arguments.length ? (domain = Array.from(_), n = Math.min(domain.length, range3.length - 1), scale) : domain.slice();
  };
  scale.range = function(_) {
    return arguments.length ? (range3 = Array.from(_), n = Math.min(domain.length, range3.length - 1), scale) : range3.slice();
  };
  scale.invertExtent = function(y2) {
    var i = range3.indexOf(y2);
    return [domain[i - 1], domain[i]];
  };
  scale.unknown = function(_) {
    return arguments.length ? (unknown = _, scale) : unknown;
  };
  scale.copy = function() {
    return threshold().domain(domain).range(range3).unknown(unknown);
  };
  return initRange.apply(scale, arguments);
}

// node_modules/d3-time/src/interval.js
var t0 = /* @__PURE__ */ new Date();
var t1 = /* @__PURE__ */ new Date();
function timeInterval(floori, offseti, count, field) {
  function interval(date2) {
    return floori(date2 = arguments.length === 0 ? /* @__PURE__ */ new Date() : /* @__PURE__ */ new Date(+date2)), date2;
  }
  interval.floor = (date2) => {
    return floori(date2 = /* @__PURE__ */ new Date(+date2)), date2;
  };
  interval.ceil = (date2) => {
    return floori(date2 = new Date(date2 - 1)), offseti(date2, 1), floori(date2), date2;
  };
  interval.round = (date2) => {
    const d0 = interval(date2), d1 = interval.ceil(date2);
    return date2 - d0 < d1 - date2 ? d0 : d1;
  };
  interval.offset = (date2, step) => {
    return offseti(date2 = /* @__PURE__ */ new Date(+date2), step == null ? 1 : Math.floor(step)), date2;
  };
  interval.range = (start, stop, step) => {
    const range3 = [];
    start = interval.ceil(start);
    step = step == null ? 1 : Math.floor(step);
    if (!(start < stop) || !(step > 0)) return range3;
    let previous;
    do
      range3.push(previous = /* @__PURE__ */ new Date(+start)), offseti(start, step), floori(start);
    while (previous < start && start < stop);
    return range3;
  };
  interval.filter = (test) => {
    return timeInterval((date2) => {
      if (date2 >= date2) while (floori(date2), !test(date2)) date2.setTime(date2 - 1);
    }, (date2, step) => {
      if (date2 >= date2) {
        if (step < 0) while (++step <= 0) {
          while (offseti(date2, -1), !test(date2)) {
          }
        }
        else while (--step >= 0) {
          while (offseti(date2, 1), !test(date2)) {
          }
        }
      }
    });
  };
  if (count) {
    interval.count = (start, end) => {
      t0.setTime(+start), t1.setTime(+end);
      floori(t0), floori(t1);
      return Math.floor(count(t0, t1));
    };
    interval.every = (step) => {
      step = Math.floor(step);
      return !isFinite(step) || !(step > 0) ? null : !(step > 1) ? interval : interval.filter(field ? (d) => field(d) % step === 0 : (d) => interval.count(0, d) % step === 0);
    };
  }
  return interval;
}

// node_modules/d3-time/src/millisecond.js
var millisecond = timeInterval(() => {
}, (date2, step) => {
  date2.setTime(+date2 + step);
}, (start, end) => {
  return end - start;
});
millisecond.every = (k) => {
  k = Math.floor(k);
  if (!isFinite(k) || !(k > 0)) return null;
  if (!(k > 1)) return millisecond;
  return timeInterval((date2) => {
    date2.setTime(Math.floor(date2 / k) * k);
  }, (date2, step) => {
    date2.setTime(+date2 + step * k);
  }, (start, end) => {
    return (end - start) / k;
  });
};
var milliseconds = millisecond.range;

// node_modules/d3-time/src/duration.js
var durationSecond = 1e3;
var durationMinute = durationSecond * 60;
var durationHour = durationMinute * 60;
var durationDay = durationHour * 24;
var durationWeek = durationDay * 7;
var durationMonth = durationDay * 30;
var durationYear = durationDay * 365;

// node_modules/d3-time/src/second.js
var second = timeInterval((date2) => {
  date2.setTime(date2 - date2.getMilliseconds());
}, (date2, step) => {
  date2.setTime(+date2 + step * durationSecond);
}, (start, end) => {
  return (end - start) / durationSecond;
}, (date2) => {
  return date2.getUTCSeconds();
});
var seconds = second.range;

// node_modules/d3-time/src/minute.js
var timeMinute = timeInterval((date2) => {
  date2.setTime(date2 - date2.getMilliseconds() - date2.getSeconds() * durationSecond);
}, (date2, step) => {
  date2.setTime(+date2 + step * durationMinute);
}, (start, end) => {
  return (end - start) / durationMinute;
}, (date2) => {
  return date2.getMinutes();
});
var timeMinutes = timeMinute.range;
var utcMinute = timeInterval((date2) => {
  date2.setUTCSeconds(0, 0);
}, (date2, step) => {
  date2.setTime(+date2 + step * durationMinute);
}, (start, end) => {
  return (end - start) / durationMinute;
}, (date2) => {
  return date2.getUTCMinutes();
});
var utcMinutes = utcMinute.range;

// node_modules/d3-time/src/hour.js
var timeHour = timeInterval((date2) => {
  date2.setTime(date2 - date2.getMilliseconds() - date2.getSeconds() * durationSecond - date2.getMinutes() * durationMinute);
}, (date2, step) => {
  date2.setTime(+date2 + step * durationHour);
}, (start, end) => {
  return (end - start) / durationHour;
}, (date2) => {
  return date2.getHours();
});
var timeHours = timeHour.range;
var utcHour = timeInterval((date2) => {
  date2.setUTCMinutes(0, 0, 0);
}, (date2, step) => {
  date2.setTime(+date2 + step * durationHour);
}, (start, end) => {
  return (end - start) / durationHour;
}, (date2) => {
  return date2.getUTCHours();
});
var utcHours = utcHour.range;

// node_modules/d3-time/src/day.js
var timeDay = timeInterval(
  (date2) => date2.setHours(0, 0, 0, 0),
  (date2, step) => date2.setDate(date2.getDate() + step),
  (start, end) => (end - start - (end.getTimezoneOffset() - start.getTimezoneOffset()) * durationMinute) / durationDay,
  (date2) => date2.getDate() - 1
);
var timeDays = timeDay.range;
var utcDay = timeInterval((date2) => {
  date2.setUTCHours(0, 0, 0, 0);
}, (date2, step) => {
  date2.setUTCDate(date2.getUTCDate() + step);
}, (start, end) => {
  return (end - start) / durationDay;
}, (date2) => {
  return date2.getUTCDate() - 1;
});
var utcDays = utcDay.range;
var unixDay = timeInterval((date2) => {
  date2.setUTCHours(0, 0, 0, 0);
}, (date2, step) => {
  date2.setUTCDate(date2.getUTCDate() + step);
}, (start, end) => {
  return (end - start) / durationDay;
}, (date2) => {
  return Math.floor(date2 / durationDay);
});
var unixDays = unixDay.range;

// node_modules/d3-time/src/week.js
function timeWeekday(i) {
  return timeInterval((date2) => {
    date2.setDate(date2.getDate() - (date2.getDay() + 7 - i) % 7);
    date2.setHours(0, 0, 0, 0);
  }, (date2, step) => {
    date2.setDate(date2.getDate() + step * 7);
  }, (start, end) => {
    return (end - start - (end.getTimezoneOffset() - start.getTimezoneOffset()) * durationMinute) / durationWeek;
  });
}
var timeSunday = timeWeekday(0);
var timeMonday = timeWeekday(1);
var timeTuesday = timeWeekday(2);
var timeWednesday = timeWeekday(3);
var timeThursday = timeWeekday(4);
var timeFriday = timeWeekday(5);
var timeSaturday = timeWeekday(6);
var timeSundays = timeSunday.range;
var timeMondays = timeMonday.range;
var timeTuesdays = timeTuesday.range;
var timeWednesdays = timeWednesday.range;
var timeThursdays = timeThursday.range;
var timeFridays = timeFriday.range;
var timeSaturdays = timeSaturday.range;
function utcWeekday(i) {
  return timeInterval((date2) => {
    date2.setUTCDate(date2.getUTCDate() - (date2.getUTCDay() + 7 - i) % 7);
    date2.setUTCHours(0, 0, 0, 0);
  }, (date2, step) => {
    date2.setUTCDate(date2.getUTCDate() + step * 7);
  }, (start, end) => {
    return (end - start) / durationWeek;
  });
}
var utcSunday = utcWeekday(0);
var utcMonday = utcWeekday(1);
var utcTuesday = utcWeekday(2);
var utcWednesday = utcWeekday(3);
var utcThursday = utcWeekday(4);
var utcFriday = utcWeekday(5);
var utcSaturday = utcWeekday(6);
var utcSundays = utcSunday.range;
var utcMondays = utcMonday.range;
var utcTuesdays = utcTuesday.range;
var utcWednesdays = utcWednesday.range;
var utcThursdays = utcThursday.range;
var utcFridays = utcFriday.range;
var utcSaturdays = utcSaturday.range;

// node_modules/d3-time/src/month.js
var timeMonth = timeInterval((date2) => {
  date2.setDate(1);
  date2.setHours(0, 0, 0, 0);
}, (date2, step) => {
  date2.setMonth(date2.getMonth() + step);
}, (start, end) => {
  return end.getMonth() - start.getMonth() + (end.getFullYear() - start.getFullYear()) * 12;
}, (date2) => {
  return date2.getMonth();
});
var timeMonths = timeMonth.range;
var utcMonth = timeInterval((date2) => {
  date2.setUTCDate(1);
  date2.setUTCHours(0, 0, 0, 0);
}, (date2, step) => {
  date2.setUTCMonth(date2.getUTCMonth() + step);
}, (start, end) => {
  return end.getUTCMonth() - start.getUTCMonth() + (end.getUTCFullYear() - start.getUTCFullYear()) * 12;
}, (date2) => {
  return date2.getUTCMonth();
});
var utcMonths = utcMonth.range;

// node_modules/d3-time/src/year.js
var timeYear = timeInterval((date2) => {
  date2.setMonth(0, 1);
  date2.setHours(0, 0, 0, 0);
}, (date2, step) => {
  date2.setFullYear(date2.getFullYear() + step);
}, (start, end) => {
  return end.getFullYear() - start.getFullYear();
}, (date2) => {
  return date2.getFullYear();
});
timeYear.every = (k) => {
  return !isFinite(k = Math.floor(k)) || !(k > 0) ? null : timeInterval((date2) => {
    date2.setFullYear(Math.floor(date2.getFullYear() / k) * k);
    date2.setMonth(0, 1);
    date2.setHours(0, 0, 0, 0);
  }, (date2, step) => {
    date2.setFullYear(date2.getFullYear() + step * k);
  });
};
var timeYears = timeYear.range;
var utcYear = timeInterval((date2) => {
  date2.setUTCMonth(0, 1);
  date2.setUTCHours(0, 0, 0, 0);
}, (date2, step) => {
  date2.setUTCFullYear(date2.getUTCFullYear() + step);
}, (start, end) => {
  return end.getUTCFullYear() - start.getUTCFullYear();
}, (date2) => {
  return date2.getUTCFullYear();
});
utcYear.every = (k) => {
  return !isFinite(k = Math.floor(k)) || !(k > 0) ? null : timeInterval((date2) => {
    date2.setUTCFullYear(Math.floor(date2.getUTCFullYear() / k) * k);
    date2.setUTCMonth(0, 1);
    date2.setUTCHours(0, 0, 0, 0);
  }, (date2, step) => {
    date2.setUTCFullYear(date2.getUTCFullYear() + step * k);
  });
};
var utcYears = utcYear.range;

// node_modules/d3-time/src/ticks.js
function ticker(year, month, week, day, hour, minute) {
  const tickIntervals = [
    [second, 1, durationSecond],
    [second, 5, 5 * durationSecond],
    [second, 15, 15 * durationSecond],
    [second, 30, 30 * durationSecond],
    [minute, 1, durationMinute],
    [minute, 5, 5 * durationMinute],
    [minute, 15, 15 * durationMinute],
    [minute, 30, 30 * durationMinute],
    [hour, 1, durationHour],
    [hour, 3, 3 * durationHour],
    [hour, 6, 6 * durationHour],
    [hour, 12, 12 * durationHour],
    [day, 1, durationDay],
    [day, 2, 2 * durationDay],
    [week, 1, durationWeek],
    [month, 1, durationMonth],
    [month, 3, 3 * durationMonth],
    [year, 1, durationYear]
  ];
  function ticks2(start, stop, count) {
    const reverse = stop < start;
    if (reverse) [start, stop] = [stop, start];
    const interval = count && typeof count.range === "function" ? count : tickInterval(start, stop, count);
    const ticks3 = interval ? interval.range(start, +stop + 1) : [];
    return reverse ? ticks3.reverse() : ticks3;
  }
  function tickInterval(start, stop, count) {
    const target = Math.abs(stop - start) / count;
    const i = bisector(([, , step2]) => step2).right(tickIntervals, target);
    if (i === tickIntervals.length) return year.every(tickStep(start / durationYear, stop / durationYear, count));
    if (i === 0) return millisecond.every(Math.max(tickStep(start, stop, count), 1));
    const [t, step] = tickIntervals[target / tickIntervals[i - 1][2] < tickIntervals[i][2] / target ? i - 1 : i];
    return t.every(step);
  }
  return [ticks2, tickInterval];
}
var [utcTicks, utcTickInterval] = ticker(utcYear, utcMonth, utcSunday, unixDay, utcHour, utcMinute);
var [timeTicks, timeTickInterval] = ticker(timeYear, timeMonth, timeSunday, timeDay, timeHour, timeMinute);

// node_modules/d3-time-format/src/locale.js
function localDate(d) {
  if (0 <= d.y && d.y < 100) {
    var date2 = new Date(-1, d.m, d.d, d.H, d.M, d.S, d.L);
    date2.setFullYear(d.y);
    return date2;
  }
  return new Date(d.y, d.m, d.d, d.H, d.M, d.S, d.L);
}
function utcDate(d) {
  if (0 <= d.y && d.y < 100) {
    var date2 = new Date(Date.UTC(-1, d.m, d.d, d.H, d.M, d.S, d.L));
    date2.setUTCFullYear(d.y);
    return date2;
  }
  return new Date(Date.UTC(d.y, d.m, d.d, d.H, d.M, d.S, d.L));
}
function newDate(y2, m, d) {
  return { y: y2, m, d, H: 0, M: 0, S: 0, L: 0 };
}
function formatLocale(locale2) {
  var locale_dateTime = locale2.dateTime, locale_date = locale2.date, locale_time = locale2.time, locale_periods = locale2.periods, locale_weekdays = locale2.days, locale_shortWeekdays = locale2.shortDays, locale_months = locale2.months, locale_shortMonths = locale2.shortMonths;
  var periodRe = formatRe(locale_periods), periodLookup = formatLookup(locale_periods), weekdayRe = formatRe(locale_weekdays), weekdayLookup = formatLookup(locale_weekdays), shortWeekdayRe = formatRe(locale_shortWeekdays), shortWeekdayLookup = formatLookup(locale_shortWeekdays), monthRe = formatRe(locale_months), monthLookup = formatLookup(locale_months), shortMonthRe = formatRe(locale_shortMonths), shortMonthLookup = formatLookup(locale_shortMonths);
  var formats = {
    "a": formatShortWeekday,
    "A": formatWeekday,
    "b": formatShortMonth,
    "B": formatMonth,
    "c": null,
    "d": formatDayOfMonth,
    "e": formatDayOfMonth,
    "f": formatMicroseconds,
    "g": formatYearISO,
    "G": formatFullYearISO,
    "H": formatHour24,
    "I": formatHour12,
    "j": formatDayOfYear,
    "L": formatMilliseconds,
    "m": formatMonthNumber,
    "M": formatMinutes,
    "p": formatPeriod,
    "q": formatQuarter,
    "Q": formatUnixTimestamp,
    "s": formatUnixTimestampSeconds,
    "S": formatSeconds,
    "u": formatWeekdayNumberMonday,
    "U": formatWeekNumberSunday,
    "V": formatWeekNumberISO,
    "w": formatWeekdayNumberSunday,
    "W": formatWeekNumberMonday,
    "x": null,
    "X": null,
    "y": formatYear,
    "Y": formatFullYear,
    "Z": formatZone,
    "%": formatLiteralPercent
  };
  var utcFormats = {
    "a": formatUTCShortWeekday,
    "A": formatUTCWeekday,
    "b": formatUTCShortMonth,
    "B": formatUTCMonth,
    "c": null,
    "d": formatUTCDayOfMonth,
    "e": formatUTCDayOfMonth,
    "f": formatUTCMicroseconds,
    "g": formatUTCYearISO,
    "G": formatUTCFullYearISO,
    "H": formatUTCHour24,
    "I": formatUTCHour12,
    "j": formatUTCDayOfYear,
    "L": formatUTCMilliseconds,
    "m": formatUTCMonthNumber,
    "M": formatUTCMinutes,
    "p": formatUTCPeriod,
    "q": formatUTCQuarter,
    "Q": formatUnixTimestamp,
    "s": formatUnixTimestampSeconds,
    "S": formatUTCSeconds,
    "u": formatUTCWeekdayNumberMonday,
    "U": formatUTCWeekNumberSunday,
    "V": formatUTCWeekNumberISO,
    "w": formatUTCWeekdayNumberSunday,
    "W": formatUTCWeekNumberMonday,
    "x": null,
    "X": null,
    "y": formatUTCYear,
    "Y": formatUTCFullYear,
    "Z": formatUTCZone,
    "%": formatLiteralPercent
  };
  var parses = {
    "a": parseShortWeekday,
    "A": parseWeekday,
    "b": parseShortMonth,
    "B": parseMonth,
    "c": parseLocaleDateTime,
    "d": parseDayOfMonth,
    "e": parseDayOfMonth,
    "f": parseMicroseconds,
    "g": parseYear,
    "G": parseFullYear,
    "H": parseHour24,
    "I": parseHour24,
    "j": parseDayOfYear,
    "L": parseMilliseconds,
    "m": parseMonthNumber,
    "M": parseMinutes,
    "p": parsePeriod,
    "q": parseQuarter,
    "Q": parseUnixTimestamp,
    "s": parseUnixTimestampSeconds,
    "S": parseSeconds,
    "u": parseWeekdayNumberMonday,
    "U": parseWeekNumberSunday,
    "V": parseWeekNumberISO,
    "w": parseWeekdayNumberSunday,
    "W": parseWeekNumberMonday,
    "x": parseLocaleDate,
    "X": parseLocaleTime,
    "y": parseYear,
    "Y": parseFullYear,
    "Z": parseZone,
    "%": parseLiteralPercent
  };
  formats.x = newFormat(locale_date, formats);
  formats.X = newFormat(locale_time, formats);
  formats.c = newFormat(locale_dateTime, formats);
  utcFormats.x = newFormat(locale_date, utcFormats);
  utcFormats.X = newFormat(locale_time, utcFormats);
  utcFormats.c = newFormat(locale_dateTime, utcFormats);
  function newFormat(specifier, formats2) {
    return function(date2) {
      var string = [], i = -1, j = 0, n = specifier.length, c, pad2, format2;
      if (!(date2 instanceof Date)) date2 = /* @__PURE__ */ new Date(+date2);
      while (++i < n) {
        if (specifier.charCodeAt(i) === 37) {
          string.push(specifier.slice(j, i));
          if ((pad2 = pads[c = specifier.charAt(++i)]) != null) c = specifier.charAt(++i);
          else pad2 = c === "e" ? " " : "0";
          if (format2 = formats2[c]) c = format2(date2, pad2);
          string.push(c);
          j = i + 1;
        }
      }
      string.push(specifier.slice(j, i));
      return string.join("");
    };
  }
  function newParse(specifier, Z) {
    return function(string) {
      var d = newDate(1900, void 0, 1), i = parseSpecifier(d, specifier, string += "", 0), week, day;
      if (i != string.length) return null;
      if ("Q" in d) return new Date(d.Q);
      if ("s" in d) return new Date(d.s * 1e3 + ("L" in d ? d.L : 0));
      if (Z && !("Z" in d)) d.Z = 0;
      if ("p" in d) d.H = d.H % 12 + d.p * 12;
      if (d.m === void 0) d.m = "q" in d ? d.q : 0;
      if ("V" in d) {
        if (d.V < 1 || d.V > 53) return null;
        if (!("w" in d)) d.w = 1;
        if ("Z" in d) {
          week = utcDate(newDate(d.y, 0, 1)), day = week.getUTCDay();
          week = day > 4 || day === 0 ? utcMonday.ceil(week) : utcMonday(week);
          week = utcDay.offset(week, (d.V - 1) * 7);
          d.y = week.getUTCFullYear();
          d.m = week.getUTCMonth();
          d.d = week.getUTCDate() + (d.w + 6) % 7;
        } else {
          week = localDate(newDate(d.y, 0, 1)), day = week.getDay();
          week = day > 4 || day === 0 ? timeMonday.ceil(week) : timeMonday(week);
          week = timeDay.offset(week, (d.V - 1) * 7);
          d.y = week.getFullYear();
          d.m = week.getMonth();
          d.d = week.getDate() + (d.w + 6) % 7;
        }
      } else if ("W" in d || "U" in d) {
        if (!("w" in d)) d.w = "u" in d ? d.u % 7 : "W" in d ? 1 : 0;
        day = "Z" in d ? utcDate(newDate(d.y, 0, 1)).getUTCDay() : localDate(newDate(d.y, 0, 1)).getDay();
        d.m = 0;
        d.d = "W" in d ? (d.w + 6) % 7 + d.W * 7 - (day + 5) % 7 : d.w + d.U * 7 - (day + 6) % 7;
      }
      if ("Z" in d) {
        d.H += d.Z / 100 | 0;
        d.M += d.Z % 100;
        return utcDate(d);
      }
      return localDate(d);
    };
  }
  function parseSpecifier(d, specifier, string, j) {
    var i = 0, n = specifier.length, m = string.length, c, parse;
    while (i < n) {
      if (j >= m) return -1;
      c = specifier.charCodeAt(i++);
      if (c === 37) {
        c = specifier.charAt(i++);
        parse = parses[c in pads ? specifier.charAt(i++) : c];
        if (!parse || (j = parse(d, string, j)) < 0) return -1;
      } else if (c != string.charCodeAt(j++)) {
        return -1;
      }
    }
    return j;
  }
  function parsePeriod(d, string, i) {
    var n = periodRe.exec(string.slice(i));
    return n ? (d.p = periodLookup.get(n[0].toLowerCase()), i + n[0].length) : -1;
  }
  function parseShortWeekday(d, string, i) {
    var n = shortWeekdayRe.exec(string.slice(i));
    return n ? (d.w = shortWeekdayLookup.get(n[0].toLowerCase()), i + n[0].length) : -1;
  }
  function parseWeekday(d, string, i) {
    var n = weekdayRe.exec(string.slice(i));
    return n ? (d.w = weekdayLookup.get(n[0].toLowerCase()), i + n[0].length) : -1;
  }
  function parseShortMonth(d, string, i) {
    var n = shortMonthRe.exec(string.slice(i));
    return n ? (d.m = shortMonthLookup.get(n[0].toLowerCase()), i + n[0].length) : -1;
  }
  function parseMonth(d, string, i) {
    var n = monthRe.exec(string.slice(i));
    return n ? (d.m = monthLookup.get(n[0].toLowerCase()), i + n[0].length) : -1;
  }
  function parseLocaleDateTime(d, string, i) {
    return parseSpecifier(d, locale_dateTime, string, i);
  }
  function parseLocaleDate(d, string, i) {
    return parseSpecifier(d, locale_date, string, i);
  }
  function parseLocaleTime(d, string, i) {
    return parseSpecifier(d, locale_time, string, i);
  }
  function formatShortWeekday(d) {
    return locale_shortWeekdays[d.getDay()];
  }
  function formatWeekday(d) {
    return locale_weekdays[d.getDay()];
  }
  function formatShortMonth(d) {
    return locale_shortMonths[d.getMonth()];
  }
  function formatMonth(d) {
    return locale_months[d.getMonth()];
  }
  function formatPeriod(d) {
    return locale_periods[+(d.getHours() >= 12)];
  }
  function formatQuarter(d) {
    return 1 + ~~(d.getMonth() / 3);
  }
  function formatUTCShortWeekday(d) {
    return locale_shortWeekdays[d.getUTCDay()];
  }
  function formatUTCWeekday(d) {
    return locale_weekdays[d.getUTCDay()];
  }
  function formatUTCShortMonth(d) {
    return locale_shortMonths[d.getUTCMonth()];
  }
  function formatUTCMonth(d) {
    return locale_months[d.getUTCMonth()];
  }
  function formatUTCPeriod(d) {
    return locale_periods[+(d.getUTCHours() >= 12)];
  }
  function formatUTCQuarter(d) {
    return 1 + ~~(d.getUTCMonth() / 3);
  }
  return {
    format: function(specifier) {
      var f = newFormat(specifier += "", formats);
      f.toString = function() {
        return specifier;
      };
      return f;
    },
    parse: function(specifier) {
      var p = newParse(specifier += "", false);
      p.toString = function() {
        return specifier;
      };
      return p;
    },
    utcFormat: function(specifier) {
      var f = newFormat(specifier += "", utcFormats);
      f.toString = function() {
        return specifier;
      };
      return f;
    },
    utcParse: function(specifier) {
      var p = newParse(specifier += "", true);
      p.toString = function() {
        return specifier;
      };
      return p;
    }
  };
}
var pads = { "-": "", "_": " ", "0": "0" };
var numberRe = /^\s*\d+/;
var percentRe = /^%/;
var requoteRe = /[\\^$*+?|[\]().{}]/g;
function pad(value, fill, width) {
  var sign = value < 0 ? "-" : "", string = (sign ? -value : value) + "", length = string.length;
  return sign + (length < width ? new Array(width - length + 1).join(fill) + string : string);
}
function requote(s) {
  return s.replace(requoteRe, "\\$&");
}
function formatRe(names) {
  return new RegExp("^(?:" + names.map(requote).join("|") + ")", "i");
}
function formatLookup(names) {
  return new Map(names.map((name, i) => [name.toLowerCase(), i]));
}
function parseWeekdayNumberSunday(d, string, i) {
  var n = numberRe.exec(string.slice(i, i + 1));
  return n ? (d.w = +n[0], i + n[0].length) : -1;
}
function parseWeekdayNumberMonday(d, string, i) {
  var n = numberRe.exec(string.slice(i, i + 1));
  return n ? (d.u = +n[0], i + n[0].length) : -1;
}
function parseWeekNumberSunday(d, string, i) {
  var n = numberRe.exec(string.slice(i, i + 2));
  return n ? (d.U = +n[0], i + n[0].length) : -1;
}
function parseWeekNumberISO(d, string, i) {
  var n = numberRe.exec(string.slice(i, i + 2));
  return n ? (d.V = +n[0], i + n[0].length) : -1;
}
function parseWeekNumberMonday(d, string, i) {
  var n = numberRe.exec(string.slice(i, i + 2));
  return n ? (d.W = +n[0], i + n[0].length) : -1;
}
function parseFullYear(d, string, i) {
  var n = numberRe.exec(string.slice(i, i + 4));
  return n ? (d.y = +n[0], i + n[0].length) : -1;
}
function parseYear(d, string, i) {
  var n = numberRe.exec(string.slice(i, i + 2));
  return n ? (d.y = +n[0] + (+n[0] > 68 ? 1900 : 2e3), i + n[0].length) : -1;
}
function parseZone(d, string, i) {
  var n = /^(Z)|([+-]\d\d)(?::?(\d\d))?/.exec(string.slice(i, i + 6));
  return n ? (d.Z = n[1] ? 0 : -(n[2] + (n[3] || "00")), i + n[0].length) : -1;
}
function parseQuarter(d, string, i) {
  var n = numberRe.exec(string.slice(i, i + 1));
  return n ? (d.q = n[0] * 3 - 3, i + n[0].length) : -1;
}
function parseMonthNumber(d, string, i) {
  var n = numberRe.exec(string.slice(i, i + 2));
  return n ? (d.m = n[0] - 1, i + n[0].length) : -1;
}
function parseDayOfMonth(d, string, i) {
  var n = numberRe.exec(string.slice(i, i + 2));
  return n ? (d.d = +n[0], i + n[0].length) : -1;
}
function parseDayOfYear(d, string, i) {
  var n = numberRe.exec(string.slice(i, i + 3));
  return n ? (d.m = 0, d.d = +n[0], i + n[0].length) : -1;
}
function parseHour24(d, string, i) {
  var n = numberRe.exec(string.slice(i, i + 2));
  return n ? (d.H = +n[0], i + n[0].length) : -1;
}
function parseMinutes(d, string, i) {
  var n = numberRe.exec(string.slice(i, i + 2));
  return n ? (d.M = +n[0], i + n[0].length) : -1;
}
function parseSeconds(d, string, i) {
  var n = numberRe.exec(string.slice(i, i + 2));
  return n ? (d.S = +n[0], i + n[0].length) : -1;
}
function parseMilliseconds(d, string, i) {
  var n = numberRe.exec(string.slice(i, i + 3));
  return n ? (d.L = +n[0], i + n[0].length) : -1;
}
function parseMicroseconds(d, string, i) {
  var n = numberRe.exec(string.slice(i, i + 6));
  return n ? (d.L = Math.floor(n[0] / 1e3), i + n[0].length) : -1;
}
function parseLiteralPercent(d, string, i) {
  var n = percentRe.exec(string.slice(i, i + 1));
  return n ? i + n[0].length : -1;
}
function parseUnixTimestamp(d, string, i) {
  var n = numberRe.exec(string.slice(i));
  return n ? (d.Q = +n[0], i + n[0].length) : -1;
}
function parseUnixTimestampSeconds(d, string, i) {
  var n = numberRe.exec(string.slice(i));
  return n ? (d.s = +n[0], i + n[0].length) : -1;
}
function formatDayOfMonth(d, p) {
  return pad(d.getDate(), p, 2);
}
function formatHour24(d, p) {
  return pad(d.getHours(), p, 2);
}
function formatHour12(d, p) {
  return pad(d.getHours() % 12 || 12, p, 2);
}
function formatDayOfYear(d, p) {
  return pad(1 + timeDay.count(timeYear(d), d), p, 3);
}
function formatMilliseconds(d, p) {
  return pad(d.getMilliseconds(), p, 3);
}
function formatMicroseconds(d, p) {
  return formatMilliseconds(d, p) + "000";
}
function formatMonthNumber(d, p) {
  return pad(d.getMonth() + 1, p, 2);
}
function formatMinutes(d, p) {
  return pad(d.getMinutes(), p, 2);
}
function formatSeconds(d, p) {
  return pad(d.getSeconds(), p, 2);
}
function formatWeekdayNumberMonday(d) {
  var day = d.getDay();
  return day === 0 ? 7 : day;
}
function formatWeekNumberSunday(d, p) {
  return pad(timeSunday.count(timeYear(d) - 1, d), p, 2);
}
function dISO(d) {
  var day = d.getDay();
  return day >= 4 || day === 0 ? timeThursday(d) : timeThursday.ceil(d);
}
function formatWeekNumberISO(d, p) {
  d = dISO(d);
  return pad(timeThursday.count(timeYear(d), d) + (timeYear(d).getDay() === 4), p, 2);
}
function formatWeekdayNumberSunday(d) {
  return d.getDay();
}
function formatWeekNumberMonday(d, p) {
  return pad(timeMonday.count(timeYear(d) - 1, d), p, 2);
}
function formatYear(d, p) {
  return pad(d.getFullYear() % 100, p, 2);
}
function formatYearISO(d, p) {
  d = dISO(d);
  return pad(d.getFullYear() % 100, p, 2);
}
function formatFullYear(d, p) {
  return pad(d.getFullYear() % 1e4, p, 4);
}
function formatFullYearISO(d, p) {
  var day = d.getDay();
  d = day >= 4 || day === 0 ? timeThursday(d) : timeThursday.ceil(d);
  return pad(d.getFullYear() % 1e4, p, 4);
}
function formatZone(d) {
  var z = d.getTimezoneOffset();
  return (z > 0 ? "-" : (z *= -1, "+")) + pad(z / 60 | 0, "0", 2) + pad(z % 60, "0", 2);
}
function formatUTCDayOfMonth(d, p) {
  return pad(d.getUTCDate(), p, 2);
}
function formatUTCHour24(d, p) {
  return pad(d.getUTCHours(), p, 2);
}
function formatUTCHour12(d, p) {
  return pad(d.getUTCHours() % 12 || 12, p, 2);
}
function formatUTCDayOfYear(d, p) {
  return pad(1 + utcDay.count(utcYear(d), d), p, 3);
}
function formatUTCMilliseconds(d, p) {
  return pad(d.getUTCMilliseconds(), p, 3);
}
function formatUTCMicroseconds(d, p) {
  return formatUTCMilliseconds(d, p) + "000";
}
function formatUTCMonthNumber(d, p) {
  return pad(d.getUTCMonth() + 1, p, 2);
}
function formatUTCMinutes(d, p) {
  return pad(d.getUTCMinutes(), p, 2);
}
function formatUTCSeconds(d, p) {
  return pad(d.getUTCSeconds(), p, 2);
}
function formatUTCWeekdayNumberMonday(d) {
  var dow = d.getUTCDay();
  return dow === 0 ? 7 : dow;
}
function formatUTCWeekNumberSunday(d, p) {
  return pad(utcSunday.count(utcYear(d) - 1, d), p, 2);
}
function UTCdISO(d) {
  var day = d.getUTCDay();
  return day >= 4 || day === 0 ? utcThursday(d) : utcThursday.ceil(d);
}
function formatUTCWeekNumberISO(d, p) {
  d = UTCdISO(d);
  return pad(utcThursday.count(utcYear(d), d) + (utcYear(d).getUTCDay() === 4), p, 2);
}
function formatUTCWeekdayNumberSunday(d) {
  return d.getUTCDay();
}
function formatUTCWeekNumberMonday(d, p) {
  return pad(utcMonday.count(utcYear(d) - 1, d), p, 2);
}
function formatUTCYear(d, p) {
  return pad(d.getUTCFullYear() % 100, p, 2);
}
function formatUTCYearISO(d, p) {
  d = UTCdISO(d);
  return pad(d.getUTCFullYear() % 100, p, 2);
}
function formatUTCFullYear(d, p) {
  return pad(d.getUTCFullYear() % 1e4, p, 4);
}
function formatUTCFullYearISO(d, p) {
  var day = d.getUTCDay();
  d = day >= 4 || day === 0 ? utcThursday(d) : utcThursday.ceil(d);
  return pad(d.getUTCFullYear() % 1e4, p, 4);
}
function formatUTCZone() {
  return "+0000";
}
function formatLiteralPercent() {
  return "%";
}
function formatUnixTimestamp(d) {
  return +d;
}
function formatUnixTimestampSeconds(d) {
  return Math.floor(+d / 1e3);
}

// node_modules/d3-time-format/src/defaultLocale.js
var locale;
var timeFormat;
var timeParse;
var utcFormat;
var utcParse;
defaultLocale({
  dateTime: "%x, %X",
  date: "%-m/%-d/%Y",
  time: "%-I:%M:%S %p",
  periods: ["AM", "PM"],
  days: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
  shortDays: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
  months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
  shortMonths: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
});
function defaultLocale(definition) {
  locale = formatLocale(definition);
  timeFormat = locale.format;
  timeParse = locale.parse;
  utcFormat = locale.utcFormat;
  utcParse = locale.utcParse;
  return locale;
}

// node_modules/d3-time-format/src/isoFormat.js
var isoSpecifier = "%Y-%m-%dT%H:%M:%S.%LZ";
function formatIsoNative(date2) {
  return date2.toISOString();
}
var formatIso = Date.prototype.toISOString ? formatIsoNative : utcFormat(isoSpecifier);

// node_modules/d3-time-format/src/isoParse.js
function parseIsoNative(string) {
  var date2 = new Date(string);
  return isNaN(date2) ? null : date2;
}
var parseIso = +/* @__PURE__ */ new Date("2000-01-01T00:00:00.000Z") ? parseIsoNative : utcParse(isoSpecifier);

// node_modules/d3-scale/src/time.js
function date(t) {
  return new Date(t);
}
function number2(t) {
  return t instanceof Date ? +t : +/* @__PURE__ */ new Date(+t);
}
function calendar(ticks2, tickInterval, year, month, week, day, hour, minute, second2, format2) {
  var scale = continuous(), invert2 = scale.invert, domain = scale.domain;
  var formatMillisecond = format2(".%L"), formatSecond = format2(":%S"), formatMinute = format2("%I:%M"), formatHour = format2("%I %p"), formatDay = format2("%a %d"), formatWeek = format2("%b %d"), formatMonth = format2("%B"), formatYear2 = format2("%Y");
  function tickFormat2(date2) {
    return (second2(date2) < date2 ? formatMillisecond : minute(date2) < date2 ? formatSecond : hour(date2) < date2 ? formatMinute : day(date2) < date2 ? formatHour : month(date2) < date2 ? week(date2) < date2 ? formatDay : formatWeek : year(date2) < date2 ? formatMonth : formatYear2)(date2);
  }
  scale.invert = function(y2) {
    return new Date(invert2(y2));
  };
  scale.domain = function(_) {
    return arguments.length ? domain(Array.from(_, number2)) : domain().map(date);
  };
  scale.ticks = function(interval) {
    var d = domain();
    return ticks2(d[0], d[d.length - 1], interval == null ? 10 : interval);
  };
  scale.tickFormat = function(count, specifier) {
    return specifier == null ? tickFormat2 : format2(specifier);
  };
  scale.nice = function(interval) {
    var d = domain();
    if (!interval || typeof interval.range !== "function") interval = tickInterval(d[0], d[d.length - 1], interval == null ? 10 : interval);
    return interval ? domain(nice(d, interval)) : scale;
  };
  scale.copy = function() {
    return copy(scale, calendar(ticks2, tickInterval, year, month, week, day, hour, minute, second2, format2));
  };
  return scale;
}
function time() {
  return initRange.apply(calendar(timeTicks, timeTickInterval, timeYear, timeMonth, timeSunday, timeDay, timeHour, timeMinute, second, timeFormat).domain([new Date(2e3, 0, 1), new Date(2e3, 0, 2)]), arguments);
}

// node_modules/d3-scale/src/utcTime.js
function utcTime() {
  return initRange.apply(calendar(utcTicks, utcTickInterval, utcYear, utcMonth, utcSunday, utcDay, utcHour, utcMinute, second, utcFormat).domain([Date.UTC(2e3, 0, 1), Date.UTC(2e3, 0, 2)]), arguments);
}

// node_modules/d3-scale/src/sequential.js
function transformer2() {
  var x0 = 0, x1 = 1, t02, t12, k10, transform, interpolator = identity, clamp = false, unknown;
  function scale(x2) {
    return x2 == null || isNaN(x2 = +x2) ? unknown : interpolator(k10 === 0 ? 0.5 : (x2 = (transform(x2) - t02) * k10, clamp ? Math.max(0, Math.min(1, x2)) : x2));
  }
  scale.domain = function(_) {
    return arguments.length ? ([x0, x1] = _, t02 = transform(x0 = +x0), t12 = transform(x1 = +x1), k10 = t02 === t12 ? 0 : 1 / (t12 - t02), scale) : [x0, x1];
  };
  scale.clamp = function(_) {
    return arguments.length ? (clamp = !!_, scale) : clamp;
  };
  scale.interpolator = function(_) {
    return arguments.length ? (interpolator = _, scale) : interpolator;
  };
  function range3(interpolate) {
    return function(_) {
      var r0, r1;
      return arguments.length ? ([r0, r1] = _, interpolator = interpolate(r0, r1), scale) : [interpolator(0), interpolator(1)];
    };
  }
  scale.range = range3(value_default);
  scale.rangeRound = range3(round_default);
  scale.unknown = function(_) {
    return arguments.length ? (unknown = _, scale) : unknown;
  };
  return function(t) {
    transform = t, t02 = t(x0), t12 = t(x1), k10 = t02 === t12 ? 0 : 1 / (t12 - t02);
    return scale;
  };
}
function copy2(source, target) {
  return target.domain(source.domain()).interpolator(source.interpolator()).clamp(source.clamp()).unknown(source.unknown());
}
function sequential() {
  var scale = linearish(transformer2()(identity));
  scale.copy = function() {
    return copy2(scale, sequential());
  };
  return initInterpolator.apply(scale, arguments);
}
function sequentialLog() {
  var scale = loggish(transformer2()).domain([1, 10]);
  scale.copy = function() {
    return copy2(scale, sequentialLog()).base(scale.base());
  };
  return initInterpolator.apply(scale, arguments);
}
function sequentialSymlog() {
  var scale = symlogish(transformer2());
  scale.copy = function() {
    return copy2(scale, sequentialSymlog()).constant(scale.constant());
  };
  return initInterpolator.apply(scale, arguments);
}
function sequentialPow() {
  var scale = powish(transformer2());
  scale.copy = function() {
    return copy2(scale, sequentialPow()).exponent(scale.exponent());
  };
  return initInterpolator.apply(scale, arguments);
}
function sequentialSqrt() {
  return sequentialPow.apply(null, arguments).exponent(0.5);
}

// node_modules/d3-scale/src/sequentialQuantile.js
function sequentialQuantile() {
  var domain = [], interpolator = identity;
  function scale(x2) {
    if (x2 != null && !isNaN(x2 = +x2)) return interpolator((bisect_default(domain, x2, 1) - 1) / (domain.length - 1));
  }
  scale.domain = function(_) {
    if (!arguments.length) return domain.slice();
    domain = [];
    for (let d of _) if (d != null && !isNaN(d = +d)) domain.push(d);
    domain.sort(ascending);
    return scale;
  };
  scale.interpolator = function(_) {
    return arguments.length ? (interpolator = _, scale) : interpolator;
  };
  scale.range = function() {
    return domain.map((d, i) => interpolator(i / (domain.length - 1)));
  };
  scale.quantiles = function(n) {
    return Array.from({ length: n + 1 }, (_, i) => quantile(domain, i / n));
  };
  scale.copy = function() {
    return sequentialQuantile(interpolator).domain(domain);
  };
  return initInterpolator.apply(scale, arguments);
}

// node_modules/d3-scale/src/diverging.js
function transformer3() {
  var x0 = 0, x1 = 0.5, x2 = 1, s = 1, t02, t12, t2, k10, k21, interpolator = identity, transform, clamp = false, unknown;
  function scale(x3) {
    return isNaN(x3 = +x3) ? unknown : (x3 = 0.5 + ((x3 = +transform(x3)) - t12) * (s * x3 < s * t12 ? k10 : k21), interpolator(clamp ? Math.max(0, Math.min(1, x3)) : x3));
  }
  scale.domain = function(_) {
    return arguments.length ? ([x0, x1, x2] = _, t02 = transform(x0 = +x0), t12 = transform(x1 = +x1), t2 = transform(x2 = +x2), k10 = t02 === t12 ? 0 : 0.5 / (t12 - t02), k21 = t12 === t2 ? 0 : 0.5 / (t2 - t12), s = t12 < t02 ? -1 : 1, scale) : [x0, x1, x2];
  };
  scale.clamp = function(_) {
    return arguments.length ? (clamp = !!_, scale) : clamp;
  };
  scale.interpolator = function(_) {
    return arguments.length ? (interpolator = _, scale) : interpolator;
  };
  function range3(interpolate) {
    return function(_) {
      var r0, r1, r2;
      return arguments.length ? ([r0, r1, r2] = _, interpolator = piecewise(interpolate, [r0, r1, r2]), scale) : [interpolator(0), interpolator(0.5), interpolator(1)];
    };
  }
  scale.range = range3(value_default);
  scale.rangeRound = range3(round_default);
  scale.unknown = function(_) {
    return arguments.length ? (unknown = _, scale) : unknown;
  };
  return function(t) {
    transform = t, t02 = t(x0), t12 = t(x1), t2 = t(x2), k10 = t02 === t12 ? 0 : 0.5 / (t12 - t02), k21 = t12 === t2 ? 0 : 0.5 / (t2 - t12), s = t12 < t02 ? -1 : 1;
    return scale;
  };
}
function diverging() {
  var scale = linearish(transformer3()(identity));
  scale.copy = function() {
    return copy2(scale, diverging());
  };
  return initInterpolator.apply(scale, arguments);
}
function divergingLog() {
  var scale = loggish(transformer3()).domain([0.1, 1, 10]);
  scale.copy = function() {
    return copy2(scale, divergingLog()).base(scale.base());
  };
  return initInterpolator.apply(scale, arguments);
}
function divergingSymlog() {
  var scale = symlogish(transformer3());
  scale.copy = function() {
    return copy2(scale, divergingSymlog()).constant(scale.constant());
  };
  return initInterpolator.apply(scale, arguments);
}
function divergingPow() {
  var scale = powish(transformer3());
  scale.copy = function() {
    return copy2(scale, divergingPow()).exponent(scale.exponent());
  };
  return initInterpolator.apply(scale, arguments);
}
function divergingSqrt() {
  return divergingPow.apply(null, arguments).exponent(0.5);
}

// node_modules/victory-core/es/victory-util/scale.js
var supportedScaleStrings = ["linear", "time", "log", "sqrt"];
function toNewName(scale) {
  const capitalize = (s) => s && s[0].toUpperCase() + s.slice(1);
  return `scale${capitalize(scale)}`;
}
function validScale(scale) {
  if (typeof scale === "function") {
    return isFunction(scale.copy) && isFunction(scale.domain) && isFunction(scale.range);
  } else if (typeof scale === "string") {
    return supportedScaleStrings.includes(scale);
  }
  return false;
}
function isScaleDefined(props, axis) {
  if (!props.scale) {
    return false;
  } else if (props.scale.x || props.scale.y) {
    return !!props.scale[axis];
  }
  return true;
}
function getScaleTypeFromProps(props, axis) {
  if (!isScaleDefined(props, axis)) {
    return void 0;
  }
  const scale = props.scale[axis] || props.scale;
  return typeof scale === "string" ? scale : getType(scale);
}
function getScaleFromDomain(props, axis) {
  let domain;
  if (props.domain && props.domain[axis]) {
    domain = props.domain[axis];
  } else if (props.domain && Array.isArray(props.domain)) {
    domain = props.domain;
  }
  if (!domain) {
    return void 0;
  }
  return containsDates(domain) ? "time" : "linear";
}
function getScaleTypeFromData(props, axis) {
  if (!props.data) {
    return "linear";
  }
  const accessor = createAccessor(props[axis]);
  const axisData = props.data.map((datum) => {
    const processedData = (0, import_isPlainObject2.default)(accessor(datum)) ? accessor(datum)[axis] : accessor(datum);
    return processedData !== void 0 ? processedData : datum[axis];
  });
  return containsDates(axisData) ? "time" : "linear";
}
function getScaleFromName(name) {
  if (validScale(name)) {
    const methodName = toNewName(name);
    return d3_scale_exports[methodName]();
  }
  return linear2();
}
function getBaseScale(props, axis) {
  const scale = getScaleFromProps(props, axis);
  if (scale) {
    return typeof scale === "string" ? getScaleFromName(scale) : scale;
  }
  const defaultScale = getScaleFromDomain(props, axis) || getScaleTypeFromData(props, axis);
  return getScaleFromName(defaultScale);
}
function getDefaultScale() {
  return linear2();
}
function getScaleFromProps(props, axis) {
  if (!isScaleDefined(props, axis)) {
    return void 0;
  }
  const scale = props.scale[axis] || props.scale;
  if (validScale(scale)) {
    return isFunction(scale) ? scale : getScaleFromName(scale);
  }
  return void 0;
}
function getScaleType(props, axis) {
  return getScaleTypeFromProps(props, axis) || getScaleTypeFromData(props, axis);
}
var DUCK_TYPES = [
  {
    name: "quantile",
    method: "quantiles"
  },
  {
    name: "log",
    method: "base"
  }
  // TODO(2214): Re-evaluate (1) duck typing approach, and (2) if duck typing,
  //   do we need a different approach? (Multiple keys? Stringifying functions?)
  // https://github.com/FormidableLabs/victory/issues/2214
  // Below are matches that don't seem to otherwise occur in Victory code base.
  // { name: "ordinal", method: "unknown" },
  // { name: "pow-sqrt", method: "exponent" },
  // { name: "quantize-threshold", method: "invertExtent" }
];
function getType(scale) {
  if (typeof scale === "string") {
    return scale;
  }
  const scaleType = DUCK_TYPES.filter((type) => {
    return scale[type.method] !== void 0;
  })[0];
  return scaleType ? scaleType.name : void 0;
}

// node_modules/victory-core/es/victory-util/immutable.js
var immutable_exports = {};
__export(immutable_exports, {
  IMMUTABLE_ITERABLE: () => IMMUTABLE_ITERABLE,
  IMMUTABLE_LIST: () => IMMUTABLE_LIST,
  IMMUTABLE_MAP: () => IMMUTABLE_MAP,
  IMMUTABLE_RECORD: () => IMMUTABLE_RECORD,
  isImmutable: () => isImmutable,
  isIterable: () => isIterable,
  isList: () => isList,
  isMap: () => isMap,
  isRecord: () => isRecord,
  shallowToJS: () => shallowToJS
});
var IMMUTABLE_ITERABLE = "@@__IMMUTABLE_ITERABLE__@@";
var IMMUTABLE_RECORD = "@@__IMMUTABLE_RECORD__@@";
var IMMUTABLE_LIST = "@@__IMMUTABLE_LIST__@@";
var IMMUTABLE_MAP = "@@__IMMUTABLE_MAP__@@";
function isIterable(x2) {
  return !!(x2 && x2[IMMUTABLE_ITERABLE]);
}
function isRecord(x2) {
  return !!(x2 && x2[IMMUTABLE_RECORD]);
}
function isImmutable(x2) {
  return isIterable(x2) || isRecord(x2);
}
function isList(x2) {
  return !!(x2 && x2[IMMUTABLE_LIST]);
}
function isMap(x2) {
  return !!(x2 && x2[IMMUTABLE_MAP]);
}
function shallowToJS(x2, whitelist) {
  return isIterable(x2) ? x2.reduce((result, curr, key) => {
    let newCurr = curr;
    if (whitelist && whitelist[key]) {
      newCurr = shallowToJS(curr);
    }
    result[key] = newCurr;
    return result;
  }, isList(x2) ? [] : {}) : x2;
}

// node_modules/victory-core/es/victory-util/data.js
function parseDatum(datum) {
  const immutableDatumWhitelist = {
    errorX: true,
    errorY: true
  };
  return isImmutable(datum) ? shallowToJS(datum, immutableDatumWhitelist) : datum;
}
function getLength(data) {
  return isIterable(data) ? data.size : data.length;
}
function generateDataArray(props, axis) {
  const propsDomain = (0, import_isPlainObject3.default)(props.domain) ? props.domain[axis] : props.domain;
  const domain = propsDomain || getBaseScale(props, axis).domain();
  const samples = props.samples || 1;
  const domainMax = Math.max(...domain);
  const domainMin = Math.min(...domain);
  const step = (domainMax - domainMin) / samples;
  const values = range2(domainMin, domainMax, step);
  return values[values.length - 1] === domainMax ? values : values.concat(domainMax);
}
function sortData(dataset, sortKey, sortOrder) {
  if (sortOrder === void 0) {
    sortOrder = "ascending";
  }
  if (!sortKey) {
    return dataset;
  }
  let formattedSortKey = sortKey;
  if (sortKey === "x" || sortKey === "y") {
    formattedSortKey = `_${sortKey}`;
  }
  const order = sortOrder === "ascending" ? "asc" : "desc";
  return (0, import_orderBy2.default)(dataset, formattedSortKey, order);
}
function cleanData(dataset, props) {
  const smallNumber = 1 / Number.MAX_SAFE_INTEGER;
  const scaleType = {
    x: getScaleType(props, "x"),
    y: getScaleType(props, "y")
  };
  if (scaleType.x !== "log" && scaleType.y !== "log") {
    return dataset;
  }
  const rules = (datum, axis) => {
    return scaleType[axis] === "log" ? datum[`_${axis}`] !== 0 : true;
  };
  const sanitize = (datum) => {
    const _x = rules(datum, "x") ? datum._x : smallNumber;
    const _y = rules(datum, "y") ? datum._y : smallNumber;
    const _y0 = rules(datum, "y0") ? datum._y0 : smallNumber;
    return Object.assign({}, datum, {
      _x,
      _y,
      _y0
    });
  };
  return dataset.map((datum) => {
    if (rules(datum, "x") && rules(datum, "y") && rules(datum, "y0")) {
      return datum;
    }
    return sanitize(datum);
  });
}
function getEventKey(key) {
  if (isFunction(key)) {
    return key;
  } else if (key === null || key === void 0) {
    return () => void 0;
  }
  return (0, import_property2.default)(key);
}
function addEventKeys(props, data) {
  const hasEventKeyAccessor = !!props.eventKey;
  const eventKeyAccessor = getEventKey(props.eventKey);
  return data.map((datum, index) => {
    if (datum.eventKey !== void 0) {
      return datum;
    } else if (hasEventKeyAccessor) {
      const eventKey = eventKeyAccessor(datum, index);
      return eventKey !== void 0 ? Object.assign({
        eventKey
      }, datum) : datum;
    }
    return datum;
  });
}
function formatDataFromDomain(dataset, domain, defaultBaseline) {
  const exists2 = (val) => val !== void 0;
  const minDomainX = getMinValue(domain.x);
  const maxDomainX = getMaxValue(domain.x);
  const minDomainY = getMinValue(domain.y);
  const maxDomainY = getMaxValue(domain.y);
  const underMin = (min2) => (val) => exists2(val) && val < min2;
  const overMax = (max2) => (val) => exists2(val) && val > max2;
  const isUnderMinX = underMin(minDomainX);
  const isUnderMinY = underMin(minDomainY);
  const isOverMaxX = overMax(maxDomainX);
  const isOverMaxY = overMax(maxDomainY);
  return dataset.map((datum) => {
    let {
      _x,
      _y,
      _y0,
      _y1
    } = datum;
    if (isUnderMinX(_x) || isOverMaxX(_x)) _x = null;
    const baseline = exists2(_y0) ? _y0 : defaultBaseline;
    const value = exists2(_y1) ? _y1 : _y;
    if (!exists2(value)) return datum;
    if (!exists2(baseline) && (isUnderMinY(value) || isOverMaxY(value))) _y = null;
    if (isUnderMinY(baseline) && isUnderMinY(value) || isOverMaxY(baseline) && isOverMaxY(value)) _y = _y0 = _y1 = null;
    if (isUnderMinY(baseline) && !isUnderMinY(value)) _y0 = minDomainY;
    if (isOverMaxY(baseline) && !isOverMaxY(value)) _y0 = maxDomainY;
    return Object.assign({}, datum, (0, import_omitBy2.default)({
      _x,
      _y,
      _y0,
      _y1
    }, import_isUndefined.default));
  });
}
function createStringMap(props, axis) {
  const stringsFromAxes = getStringsFromAxes(props, axis);
  const stringsFromCategories = getStringsFromCategories(props, axis);
  const stringsFromData = getStringsFromData(props, axis);
  const allStrings = (0, import_uniq2.default)([...stringsFromAxes, ...stringsFromCategories, ...stringsFromData]);
  return allStrings.length === 0 ? null : allStrings.reduce((memo, string, index) => {
    memo[string] = index + 1;
    return memo;
  }, {});
}
function downsample(data, maxPoints, startingIndex) {
  if (startingIndex === void 0) {
    startingIndex = 0;
  }
  const dataLength = getLength(data);
  if (dataLength > maxPoints) {
    const k = Math.pow(2, Math.ceil(Math.log2(dataLength / maxPoints)));
    return data.filter(
      // ensure modulo is always calculated from same reference: i + startingIndex
      (d, i) => (i + startingIndex) % k === 0
    );
  }
  return data;
}
function formatData(dataset, props, expectedKeys) {
  const isArrayOrIterable = Array.isArray(dataset) || isIterable(dataset);
  if (!isArrayOrIterable || getLength(dataset) < 1) {
    return [];
  }
  const defaultKeys = ["x", "y", "y0"];
  expectedKeys = Array.isArray(expectedKeys) ? expectedKeys : defaultKeys;
  const createAccessor2 = (name) => {
    return createAccessor(props[name] !== void 0 ? props[name] : name);
  };
  const accessor = expectedKeys.reduce((memo, type) => {
    memo[type] = createAccessor2(type);
    return memo;
  }, {});
  const preformattedData = (0, import_isEqual.default)(expectedKeys, defaultKeys) && props.x === "_x" && props.y === "_y" && props.y0 === "_y0";
  let stringMap;
  if (preformattedData === false) {
    stringMap = {
      x: expectedKeys.indexOf("x") !== -1 ? createStringMap(props, "x") : void 0,
      y: expectedKeys.indexOf("y") !== -1 ? createStringMap(props, "y") : void 0,
      y0: expectedKeys.indexOf("y0") !== -1 ? createStringMap(props, "y") : void 0
    };
  }
  const data = preformattedData ? dataset : dataset.reduce((dataArr, datum, index) => {
    const parsedDatum = parseDatum(datum);
    const fallbackValues = {
      x: index,
      y: parsedDatum
    };
    const processedValues = expectedKeys.reduce((memo, type) => {
      const processedValue = accessor[type](parsedDatum);
      const value = processedValue !== void 0 ? processedValue : fallbackValues[type];
      if (value !== void 0) {
        if (typeof value === "string" && stringMap[type]) {
          memo[`${type}Name`] = value;
          memo[`_${type}`] = stringMap[type][value];
        } else {
          memo[`_${type}`] = value;
        }
      }
      return memo;
    }, {});
    const formattedDatum = Object.assign({}, processedValues, parsedDatum);
    if (!(0, import_isEmpty3.default)(formattedDatum)) {
      dataArr.push(formattedDatum);
    }
    return dataArr;
  }, []);
  const sortedData = sortData(data, props.sortKey, props.sortOrder);
  const cleanedData = cleanData(sortedData, props);
  return addEventKeys(props, cleanedData);
}
function generateData(props) {
  const xValues = generateDataArray(props, "x");
  const yValues = generateDataArray(props, "y");
  const values = xValues.map((x2, i) => {
    return {
      x: x2,
      y: yValues[i]
    };
  });
  return values;
}
function getCategories(props, axis) {
  return props.categories && !Array.isArray(props.categories) ? props.categories[axis] : props.categories;
}
function getData(props) {
  return props.data ? formatData(props.data, props) : formatData(generateData(props), props);
}
function getStringsFromAxes(props, axis) {
  const {
    tickValues,
    tickFormat: tickFormat2
  } = props;
  let tickValueArray;
  if (!tickValues || !Array.isArray(tickValues) && !tickValues[axis]) {
    tickValueArray = tickFormat2 && Array.isArray(tickFormat2) ? tickFormat2 : [];
  } else {
    tickValueArray = tickValues[axis] || tickValues;
  }
  return tickValueArray.filter((val) => typeof val === "string");
}
function getStringsFromCategories(props, axis) {
  if (!props.categories) {
    return [];
  }
  const categories = getCategories(props, axis);
  const categoryStrings = categories && categories.filter((val) => typeof val === "string");
  return categoryStrings ? removeUndefined(categoryStrings) : [];
}
function getStringsFromData(props, axis) {
  const isArrayOrIterable = Array.isArray(props.data) || isIterable(props.data);
  if (!isArrayOrIterable) {
    return [];
  }
  const key = props[axis] === void 0 ? axis : props[axis];
  const accessor = createAccessor(key);
  const data = props.data.reduce((memo, d) => {
    memo.push(parseDatum(d));
    return memo;
  }, []);
  const sortedData = sortData(data, props.sortKey, props.sortOrder);
  const dataStrings = sortedData.reduce((dataArr, datum) => {
    const parsedDatum = parseDatum(datum);
    dataArr.push(accessor(parsedDatum));
    return dataArr;
  }, []).filter((datum) => typeof datum === "string");
  return dataStrings.reduce((prev, curr) => {
    if (curr !== void 0 && curr !== null && prev.indexOf(curr) === -1) {
      prev.push(curr);
    }
    return prev;
  }, []);
}
function isDataComponent(component) {
  const getRole = (child) => {
    return child && child.type ? child.type.role : "";
  };
  let role = getRole(component);
  if (role === "portal") {
    const children = import_react9.default.Children.toArray(component.props.children);
    role = children.length ? getRole(children[0]) : "";
  }
  const whitelist = ["area", "bar", "boxplot", "candlestick", "errorbar", "group", "histogram", "line", "pie", "scatter", "stack", "voronoi"];
  return whitelist.includes(role);
}

// node_modules/victory-core/es/victory-util/domain.js
function cleanDomain(domain, props, axis) {
  const scaleType = getScaleType(props, axis);
  if (scaleType !== "log") {
    return domain;
  }
  const rules = (dom) => {
    const almostZero = dom[0] < 0 || dom[1] < 0 ? -1 / Number.MAX_SAFE_INTEGER : 1 / Number.MAX_SAFE_INTEGER;
    const domainOne = dom[0] === 0 ? almostZero : dom[0];
    const domainTwo = dom[1] === 0 ? almostZero : dom[1];
    return [domainOne, domainTwo];
  };
  return rules(domain);
}
function getDomainPadding(props, axis) {
  const formatPadding = (padding2) => {
    return Array.isArray(padding2) ? {
      left: padding2[0],
      right: padding2[1]
    } : {
      left: padding2,
      right: padding2
    };
  };
  return (0, import_isPlainObject4.default)(props.domainPadding) ? formatPadding(props.domainPadding[axis]) : formatPadding(props.domainPadding);
}
function getFlatData(dataset, axis) {
  const axisKey = `_${axis}`;
  return dataset.flat().map((datum) => {
    return datum[axisKey] && datum[axisKey][1] !== void 0 ? datum[axisKey][1] : datum[axisKey];
  });
}
function getExtremeFromData(dataset, axis, type) {
  if (type === void 0) {
    type = "min";
  }
  const getExtreme = (arr) => type === "max" ? Math.max(...arr) : Math.min(...arr);
  const initialValue = type === "max" ? -Infinity : Infinity;
  let containsDate = false;
  const result = dataset.flat().reduce((memo, datum) => {
    const current0 = datum[`_${axis}0`] !== void 0 ? datum[`_${axis}0`] : datum[`_${axis}`];
    const current1 = datum[`_${axis}1`] !== void 0 ? datum[`_${axis}1`] : datum[`_${axis}`];
    const current = getExtreme([current0, current1]);
    containsDate = containsDate || current0 instanceof Date || current1 instanceof Date;
    return getExtreme([memo, current]);
  }, initialValue);
  return containsDate ? new Date(result) : result;
}
function padDomain(domain, props, axis) {
  if (!props.domainPadding) {
    return domain;
  }
  const minDomain = getMinFromProps(props, axis);
  const maxDomain = getMaxFromProps(props, axis);
  const padding2 = getDomainPadding(props, axis);
  if (!padding2.left && !padding2.right) {
    return domain;
  }
  const min2 = getMinValue(domain);
  const max2 = getMaxValue(domain);
  const currentAxis = getCurrentAxis(axis, props.horizontal);
  const range3 = getRange(props, currentAxis);
  const rangeExtent = Math.abs(range3[0] - range3[1]);
  const paddedRangeExtent = Math.max(rangeExtent - padding2.left - padding2.right, 1);
  const paddedDomainExtent = Math.abs(max2.valueOf() - min2.valueOf()) / paddedRangeExtent * rangeExtent;
  const simplePadding = {
    left: paddedDomainExtent * padding2.left / rangeExtent,
    right: paddedDomainExtent * padding2.right / rangeExtent
  };
  let paddedDomain = {
    min: min2.valueOf() - simplePadding.left,
    max: max2.valueOf() + simplePadding.right
  };
  const singleQuadrantDomainPadding = (0, import_isPlainObject4.default)(props.singleQuadrantDomainPadding) ? props.singleQuadrantDomainPadding[axis] : props.singleQuadrantDomainPadding;
  const addsQuadrants = min2 >= 0 && paddedDomain.min <= 0 || max2 <= 0 && paddedDomain.max >= 0;
  const adjust = (val, type) => {
    const coerce = type === "min" && min2 >= 0 && val <= 0 || type === "max" && max2 <= 0 && val >= 0;
    return coerce ? 0 : val;
  };
  if (addsQuadrants && singleQuadrantDomainPadding !== false) {
    const initialPadding = {
      // @ts-expect-error `max/min` might be dates
      left: Math.abs(max2 - min2) * padding2.left / rangeExtent,
      // @ts-expect-error `max/min` might be dates
      right: Math.abs(max2 - min2) * padding2.right / rangeExtent
    };
    const adjustedDomain = {
      min: adjust(min2.valueOf() - initialPadding.left, "min"),
      max: adjust(max2.valueOf() + initialPadding.right, "max")
    };
    const finalPadding = {
      left: Math.abs(adjustedDomain.max - adjustedDomain.min) * padding2.left / rangeExtent,
      right: Math.abs(adjustedDomain.max - adjustedDomain.min) * padding2.right / rangeExtent
    };
    paddedDomain = {
      min: adjust(min2.valueOf() - finalPadding.left, "min"),
      max: adjust(max2.valueOf() + finalPadding.right, "max")
    };
  }
  const finalDomain = {
    min: minDomain !== void 0 ? minDomain : paddedDomain.min,
    max: maxDomain !== void 0 ? maxDomain : paddedDomain.max
  };
  return min2 instanceof Date || max2 instanceof Date ? getDomainFromMinMax(new Date(finalDomain.min), new Date(finalDomain.max)) : getDomainFromMinMax(finalDomain.min, finalDomain.max);
}
function createDomainFunction(getDomainFromDataFunction, formatDomainFunction) {
  const getDomainFromDataFn = isFunction(getDomainFromDataFunction) ? getDomainFromDataFunction : getDomainFromData;
  const formatDomainFn = isFunction(formatDomainFunction) ? formatDomainFunction : formatDomain;
  return (props, axis) => {
    const propsDomain = getDomainFromProps(props, axis);
    if (propsDomain) {
      return formatDomainFn(propsDomain, props, axis);
    }
    const categories = getCategories(props, axis);
    const domain = categories ? getDomainFromCategories(props, axis, categories) : getDomainFromDataFn(props, axis);
    return domain ? formatDomainFn(domain, props, axis) : void 0;
  };
}
function formatDomain(domain, props, axis) {
  return cleanDomain(padDomain(domain, props, axis), props, axis);
}
function getDomain(props, axis) {
  return createDomainFunction()(props, axis);
}
function getDomainFromCategories(props, axis, categories) {
  const categoriesArray = categories || getCategories(props, axis);
  const {
    polar,
    startAngle = 0,
    endAngle = 360
  } = props;
  if (!categoriesArray) {
    return void 0;
  }
  const minDomain = getMinFromProps(props, axis);
  const maxDomain = getMaxFromProps(props, axis);
  const stringArray = containsStrings(categoriesArray) ? getStringsFromCategories(props, axis) : [];
  const stringMap = stringArray.length === 0 ? null : stringArray.reduce((memo, string, index) => {
    memo[string] = index + 1;
    return memo;
  }, {});
  const categoryValues = stringMap ? categoriesArray.map((value) => stringMap[value]) : categoriesArray;
  const min2 = minDomain !== void 0 ? minDomain : getMinValue(categoryValues);
  const max2 = maxDomain !== void 0 ? maxDomain : getMaxValue(categoryValues);
  const categoryDomain = getDomainFromMinMax(min2, max2);
  return polar && axis === "x" && Math.abs(startAngle - endAngle) === 360 ? getSymmetricDomain(categoryDomain, categoryValues) : categoryDomain;
}
function getDomainFromData(props, axis, dataset) {
  const datasetArray = dataset || getData(props);
  const {
    polar,
    startAngle = 0,
    endAngle = 360
  } = props;
  const minDomain = getMinFromProps(props, axis);
  const maxDomain = getMaxFromProps(props, axis);
  if (datasetArray.length < 1) {
    return minDomain !== void 0 && maxDomain !== void 0 ? getDomainFromMinMax(minDomain, maxDomain) : void 0;
  }
  const min2 = minDomain !== void 0 ? minDomain : getExtremeFromData(datasetArray, axis, "min");
  const max2 = maxDomain !== void 0 ? maxDomain : getExtremeFromData(datasetArray, axis, "max");
  const domain = getDomainFromMinMax(min2, max2);
  return polar && axis === "x" && Math.abs(startAngle - endAngle) === 360 ? getSymmetricDomain(domain, getFlatData(datasetArray, axis)) : domain;
}
function getDomainFromMinMax(min2, max2) {
  const getSinglePointDomain = (val) => {
    const verySmallNumber = (
      // eslint-disable-next-line no-magic-numbers
      val === 0 ? 2 * Math.pow(10, -10) : Math.pow(10, -10)
    );
    const verySmallDate = 1;
    const minVal = val instanceof Date ? new Date(Number(val) - verySmallDate) : Number(val) - verySmallNumber;
    const maxVal = val instanceof Date ? new Date(Number(val) + verySmallDate) : Number(val) + verySmallNumber;
    return val === 0 ? [0, maxVal] : [minVal, maxVal];
  };
  return Number(min2) === Number(max2) ? getSinglePointDomain(max2) : [min2, max2];
}
function getDomainFromProps(props, axis) {
  const minDomain = getMinFromProps(props, axis);
  const maxDomain = getMaxFromProps(props, axis);
  if ((0, import_isPlainObject4.default)(props.domain) && props.domain[axis]) {
    return props.domain[axis];
  } else if (Array.isArray(props.domain)) {
    return props.domain;
  } else if (minDomain !== void 0 && maxDomain !== void 0) {
    return getDomainFromMinMax(minDomain, maxDomain);
  }
  return void 0;
}
function getDomainWithZero(props, axis) {
  const propsDomain = getDomainFromProps(props, axis);
  if (propsDomain) {
    return propsDomain;
  }
  const dataset = getData(props);
  const y0Min = dataset.reduce((min2, datum) => datum._y0 < min2 ? datum._y0 : min2, Infinity);
  const ensureZero = (domain) => {
    if (axis === "x") {
      return domain;
    }
    const defaultMin = y0Min !== Infinity ? y0Min : 0;
    const maxDomainProp = getMaxFromProps(props, axis);
    const minDomainProp = getMinFromProps(props, axis);
    const max2 = maxDomainProp !== void 0 ? maxDomainProp : getMaxValue(domain, defaultMin);
    const min2 = minDomainProp !== void 0 ? minDomainProp : getMinValue(domain, defaultMin);
    return getDomainFromMinMax(min2, max2);
  };
  const getDomainFunction = () => {
    return getDomainFromData(props, axis, dataset);
  };
  const formatDomainFunction = (domain) => {
    return formatDomain(ensureZero(domain), props, axis);
  };
  return createDomainFunction(getDomainFunction, formatDomainFunction)(props, axis);
}
function getMaxFromProps(props, axis) {
  if ((0, import_isPlainObject4.default)(props.maxDomain) && props.maxDomain[axis] !== void 0) {
    return props.maxDomain[axis];
  }
  return typeof props.maxDomain === "number" || (0, import_isDate.default)(props.maxDomain) ? props.maxDomain : void 0;
}
function getMinFromProps(props, axis) {
  if ((0, import_isPlainObject4.default)(props.minDomain) && props.minDomain[axis] !== void 0) {
    return props.minDomain[axis];
  }
  return typeof props.minDomain === "number" || (0, import_isDate.default)(props.minDomain) ? props.minDomain : void 0;
}
function getSymmetricDomain(domain, values) {
  const processedData = (0, import_sortedUniq.default)(values.sort((a, b) => a - b));
  const step = processedData[1] - processedData[0];
  return [domain[0], domain[1] + step];
}
function isDomainComponent(component) {
  const getRole = (child) => {
    return child && child.type ? child.type.role : "";
  };
  let role = getRole(component);
  if (role === "portal") {
    const children = import_react10.default.Children.toArray(component.props.children);
    role = children.length ? getRole(children[0]) : "";
  }
  const whitelist = ["area", "axis", "bar", "boxplot", "candlestick", "errorbar", "group", "histogram", "line", "pie", "scatter", "stack", "voronoi"];
  return whitelist.includes(role);
}

// node_modules/victory-core/es/victory-util/axis.js
function identity3(value) {
  return value;
}
function getAxis(props) {
  const {
    dependentAxis
  } = props;
  return dependentAxis ? "y" : "x";
}
function findAxisComponents(childComponents, predicate) {
  const predicateFunction = predicate || identity3;
  const findAxes = (children) => {
    return children.reduce((memo, child) => {
      if (child.type && child.type.role === "axis" && predicateFunction(child)) {
        return memo.concat(child);
      } else if (child.props && child.props.children) {
        return memo.concat(findAxes(import_react11.default.Children.toArray(child.props.children)));
      }
      return memo;
    }, []);
  };
  return findAxes(childComponents);
}
function getAxisComponent(childComponents, axis) {
  const matchesAxis = (component) => {
    const type = component.type.getAxis(component.props);
    return type === axis;
  };
  return findAxisComponents(childComponents, matchesAxis)[0];
}
function getAxisComponentsWithParent(childComponents, type) {
  const matchesType = (child) => {
    return type === "dependent" ? child.props.dependentAxis : !child.props.dependentAxis;
  };
  const findComponents = (children) => {
    return children.reduce((memo, child) => {
      if (child.type && child.type.role === "axis" && matchesType(child)) {
        return memo.concat(child);
      } else if (child.props && child.props.children) {
        const childAxis = findComponents(import_react11.default.Children.toArray(child.props.children));
        return childAxis.length > 0 ? memo.concat(child) : memo;
      }
      return memo;
    }, []);
  };
  return findComponents(childComponents);
}
function getOrigin(domain) {
  const getSingleOrigin = (d) => {
    const domainMin = Math.min(...d);
    const domainMax = Math.max(...d);
    return domainMax < 0 ? domainMax : Math.max(0, domainMin);
  };
  return {
    x: containsDates(domain.x) ? new Date(Math.min(...domain.x)) : getSingleOrigin(domain.x),
    y: containsDates(domain.y) ? new Date(Math.min(...domain.y)) : getSingleOrigin(domain.y)
  };
}
function getOriginSign(origin, domain) {
  const getSign = () => {
    return origin <= 0 && Math.max(...domain) <= 0 ? "negative" : "positive";
  };
  return containsDates(domain) ? "positive" : getSign();
}
function isVertical(props) {
  const orientation = props.orientation || (props.dependentAxis ? "left" : "bottom");
  const vertical = {
    top: false,
    bottom: false,
    left: true,
    right: true
  };
  return vertical[orientation];
}
function stringTicks(props) {
  return props.tickValues !== void 0 && containsStrings(props.tickValues);
}
function getDefaultTickFormat(props) {
  const {
    tickValues
  } = props;
  const axis = getAxis(props);
  const stringMap = props.stringMap && props.stringMap[axis];
  const fallbackFormat = tickValues && !containsDates(tickValues) ? (x2) => x2 : void 0;
  if (!stringMap) {
    return stringTicks(props) ? (x2, index) => tickValues[index] : fallbackFormat;
  }
  const invertedStringMap = stringMap && invert(stringMap);
  const tickValueArray = (0, import_orderBy3.default)(Object.values(stringMap), (n) => n);
  const dataNames = tickValueArray.map((tick) => invertedStringMap[tick]);
  const dataTicks = ["", ...dataNames, ""];
  return (x2) => dataTicks[x2];
}
function getStringTicks(props) {
  const axis = getAxis(props);
  const stringMap = props.stringMap && props.stringMap[axis];
  const categories = Array.isArray(props.categories) ? props.categories : props.categories && props.categories[axis];
  const ticksFromCategories = categories && containsOnlyStrings(categories) ? categories.map((tick) => stringMap[tick]) : void 0;
  const ticksFromStringMap = stringMap && Object.values(stringMap);
  return ticksFromCategories && ticksFromCategories.length !== 0 ? ticksFromCategories : ticksFromStringMap;
}
function getTickArray(props) {
  const {
    tickValues,
    tickFormat: tickFormat2
  } = props;
  if ((tickValues == null ? void 0 : tickValues.length) === 0) {
    return [];
  }
  const axis = getAxis(props);
  const stringMap = props.stringMap && props.stringMap[axis];
  const getTicksFromFormat = () => {
    if (!tickFormat2 || !Array.isArray(tickFormat2)) {
      return void 0;
    }
    return containsStrings(tickFormat2) ? tickFormat2.map((t, i) => i) : tickFormat2;
  };
  let ticks2 = tickValues;
  if (stringMap) {
    ticks2 = getStringTicks(props);
  }
  if (tickValues && containsStrings(tickValues)) {
    ticks2 = stringMap ? tickValues.map((tick) => stringMap[tick]) : range2(1, tickValues.length + 1);
  }
  const tickArray = ticks2 ? (0, import_uniq3.default)(ticks2) : getTicksFromFormat();
  const buildTickArray = (arr) => {
    const newTickArray = [];
    const domain = props.domain && props.domain[axis] || props.domain;
    if (arr) {
      arr.forEach((t, index) => {
        if (Array.isArray(domain)) {
          if (t >= getMinValue(domain) && t <= getMaxValue(domain)) {
            newTickArray.push({
              value: t,
              index
            });
          }
        } else {
          newTickArray.push({
            value: t,
            index
          });
        }
      });
      return newTickArray;
    }
    return void 0;
  };
  return Array.isArray(tickArray) && tickArray.length ? buildTickArray(tickArray) : void 0;
}
function getTickFormat(props, scale) {
  const {
    tickFormat: tickFormat2
  } = props;
  const axis = getAxis(props);
  const stringMap = props.stringMap && props.stringMap[axis];
  if (!tickFormat2) {
    const defaultTickFormat = getDefaultTickFormat(props);
    const scaleTickFormat = scale.tickFormat && isFunction(scale.tickFormat) ? scale.tickFormat() : (x2) => x2;
    return defaultTickFormat || scaleTickFormat;
  } else if (tickFormat2 && Array.isArray(tickFormat2)) {
    const tickArray = getTickArray(props);
    const tickArrayIndices = tickArray == null ? void 0 : tickArray.map((v) => v.index);
    const filteredTickFormat = tickFormat2.filter((t, index) => tickArrayIndices == null ? void 0 : tickArrayIndices.includes(index));
    return (x2, index) => filteredTickFormat[index];
  } else if (tickFormat2 && isFunction(tickFormat2)) {
    const applyStringTicks = (tick, index, ticks2) => {
      const invertedStringMap = invert(stringMap);
      const stringTickArray = ticks2.map((t) => invertedStringMap[t]);
      return props.tickFormat(invertedStringMap[tick], index, stringTickArray);
    };
    return stringMap ? applyStringTicks : tickFormat2;
  }
  return (x2) => x2;
}
function downsampleTicks(ticks2, tickCount) {
  if (!tickCount || !Array.isArray(ticks2) || ticks2.length <= tickCount) {
    return ticks2;
  }
  const k = Math.floor(ticks2.length / tickCount);
  return ticks2.filter((d, i) => i % k === 0);
}
function getTicks(props, scale, filterZero) {
  if (filterZero === void 0) {
    filterZero = false;
  }
  const {
    tickCount
  } = props;
  const tickArray = getTickArray(props);
  if ((tickArray == null ? void 0 : tickArray.length) === 0) {
    return [""];
  }
  const tickValues = tickArray ? tickArray.map((v) => v.value) : void 0;
  if (tickValues) {
    return downsampleTicks(tickValues, tickCount);
  } else if (scale.ticks && isFunction(scale.ticks)) {
    const defaultTickCount = tickCount || 5;
    const scaleTicks = scale.ticks(defaultTickCount);
    const scaledTickArray = Array.isArray(scaleTicks) && scaleTicks.length ? scaleTicks : scale.domain();
    const ticks2 = downsampleTicks(scaledTickArray, tickCount);
    if (filterZero) {
      const filteredTicks = ticks2.filter((value) => value !== 0);
      return filteredTicks.length ? filteredTicks : ticks2;
    }
    return ticks2;
  }
  return scale.domain();
}
function getDomainFromData2(props, axis) {
  const {
    polar,
    startAngle = 0,
    endAngle = 360
  } = props;
  const tickArray = getTickArray(props);
  const tickValues = tickArray && (tickArray == null ? void 0 : tickArray.length) !== 0 ? tickArray.map((v) => v.value) : void 0;
  if (!Array.isArray(tickValues)) {
    return void 0;
  }
  const minDomain = getMinFromProps(props, axis);
  const maxDomain = getMaxFromProps(props, axis);
  const tickStrings = stringTicks(props);
  const ticks2 = tickValues.map((value) => Number(value));
  const defaultMin = tickStrings ? 1 : getMinValue(ticks2);
  const defaultMax = tickStrings ? tickValues.length : getMaxValue(ticks2);
  const min2 = minDomain !== void 0 ? minDomain : defaultMin;
  const max2 = maxDomain !== void 0 ? maxDomain : defaultMax;
  const initialDomain = getDomainFromMinMax(min2, max2);
  const domain = polar && axis === "x" && Math.abs(startAngle - endAngle) === 360 ? getSymmetricDomain(initialDomain, ticks2) : initialDomain;
  if (isVertical(props) && !polar) {
    domain.reverse();
  }
  return domain;
}
function getDomain2(props, axis) {
  const inherentAxis = getAxis(props);
  if (axis && axis !== inherentAxis) {
    return void 0;
  }
  return createDomainFunction(getDomainFromData2)(props, inherentAxis);
}
function getAxisValue(props, axis) {
  if (!props.axisValue) {
    return void 0;
  }
  const scaleAxis = axis === "x" ? "y" : "x";
  const scale = (0, import_isObject.default)(props.scale) && isFunction(props.scale[scaleAxis]) ? props.scale[scaleAxis] : void 0;
  if (!scale) {
    return void 0;
  }
  const stringMapAxis = axis === "x" ? "y" : "x";
  const stringMap = (0, import_isObject.default)(props.stringMap) && props.stringMap[stringMapAxis];
  const axisValue = stringMap && typeof props.axisValue === "string" ? stringMap[props.axisValue] : props.axisValue;
  return scale(axisValue);
}
function modifyProps2(props, fallbackProps22) {
  if (!(0, import_isObject.default)(props.theme)) {
    return modifyProps(props, fallbackProps22, "axis");
  }
  let role = "axis";
  if (props.dependentAxis && props.theme.dependentAxis) {
    role = "dependentAxis";
  } else if (!props.dependentAxis && props.theme.independentAxis) {
    role = "independentAxis";
  }
  if (role === "axis") {
    return modifyProps(props, fallbackProps22, "axis");
  }
  const axisTheme = (0, import_defaults5.default)({}, props.theme[role], props.theme.axis);
  const theme = Object.assign({}, props.theme, {
    axis: axisTheme
  });
  return modifyProps(Object.assign({}, props, {
    theme
  }), fallbackProps22, "axis");
}

// node_modules/victory-core/es/victory-util/default-transitions.js
var default_transitions_exports = {};
__export(default_transitions_exports, {
  continuousPolarTransitions: () => continuousPolarTransitions,
  continuousTransitions: () => continuousTransitions,
  discreteTransitions: () => discreteTransitions
});
function continuousTransitions() {
  return {
    onLoad: {
      duration: 2e3
    },
    onExit: {
      duration: 500
    },
    onEnter: {
      duration: 500
    }
  };
}
function continuousPolarTransitions() {
  return {
    onLoad: {
      duration: 2e3,
      before: () => ({
        _y: 0,
        _y1: 0,
        _y0: 0
      }),
      after: (datum) => ({
        _y: datum._y,
        _y1: datum._y1,
        _y0: datum._y0
      })
    },
    onExit: {
      duration: 500,
      before: (datum, index, data) => {
        const adjacent = (attr) => {
          const adj = index === 0 ? data[index + 1] : data[index - 1];
          return adj[attr];
        };
        return {
          _x: adjacent("_x"),
          _y: adjacent("_y"),
          _y0: adjacent("_y0")
        };
      }
    },
    onEnter: {
      duration: 500,
      before: (datum, index, data) => {
        const adjacent = (attr) => {
          const adj = index === 0 ? data[index + 1] : data[index - 1];
          return adj[attr];
        };
        return {
          _x: adjacent("_x"),
          _y: adjacent("_y"),
          _y0: adjacent("_y0")
        };
      },
      after: (datum) => ({
        _x: datum._x,
        _y: datum._y,
        _y1: datum._y1,
        _y0: datum._y0
      })
    }
  };
}
function discreteTransitions() {
  return {
    onLoad: {
      duration: 2e3,
      before: () => ({
        opacity: 0
      }),
      after: (datum) => datum
    },
    onExit: {
      duration: 600,
      before: () => ({
        opacity: 0
      })
    },
    onEnter: {
      duration: 600,
      before: () => ({
        opacity: 0
      }),
      after: (datum) => datum
    }
  };
}

// node_modules/victory-core/es/victory-util/hooks/index.js
var hooks_exports = {};
__export(hooks_exports, {
  useAnimationState: () => useAnimationState,
  usePreviousProps: () => usePreviousProps
});

// node_modules/victory-core/es/victory-util/hooks/use-previous-props.js
var import_react12 = __toESM(require_react());
function usePreviousProps(props) {
  const ref = import_react12.default.useRef();
  import_react12.default.useEffect(() => {
    ref.current = props;
  });
  return ref.current;
}

// node_modules/victory-core/es/victory-util/hooks/use-animation-state.js
var import_defaults6 = __toESM(require_defaults());
var import_react13 = __toESM(require_react());
var INITIAL_STATE = {
  nodesShouldLoad: false,
  nodesDoneLoad: false,
  animating: true
};
var useAnimationState = function(initialState) {
  if (initialState === void 0) {
    initialState = INITIAL_STATE;
  }
  const [state, _setState] = import_react13.default.useState(initialState);
  const setState = import_react13.default.useCallback((newState) => {
    _setState((oldState) => ({
      ...oldState,
      ...newState
    }));
  }, [_setState]);
  const getAnimationProps = import_react13.default.useCallback((props, child, index) => {
    if (!(props == null ? void 0 : props.animate)) {
      return child.props.animate;
    }
    const getFilteredState = () => {
      let childrenTransitions = state && state.childrenTransitions;
      childrenTransitions = isArrayOfArrays(childrenTransitions) ? childrenTransitions[index] : childrenTransitions;
      return (0, import_defaults6.default)({
        childrenTransitions
      }, state);
    };
    let getTransitions = props.animate && props.animate.getTransitions;
    const filteredState = getFilteredState();
    const parentState = props.animate && props.animate.parentState || filteredState;
    if (!getTransitions) {
      const getTransitionProps = getTransitionPropsFactory(props, filteredState, (newState) => setState(newState));
      getTransitions = (childComponent) => getTransitionProps(childComponent, index);
    }
    return (0, import_defaults6.default)({
      getTransitions,
      parentState
    }, props.animate, child.props.animate);
  }, [state, setState]);
  const setAnimationState = import_react13.default.useCallback((props, nextProps) => {
    if (!(props == null ? void 0 : props.animate)) {
      return;
    }
    if (props.animate.parentState) {
      const nodesWillExit = props.animate.parentState.nodesWillExit;
      const oldProps = nodesWillExit ? props : null;
      const newState = (0, import_defaults6.default)({
        oldProps,
        nextProps
      }, props.animate.parentState);
      setState(newState);
    } else {
      const oldChildren = import_react13.default.Children.toArray(props.children);
      const nextChildren = import_react13.default.Children.toArray(nextProps.children);
      const isContinuous = (child) => {
        const check = (c) => c.type && c.type.continuous;
        return Array.isArray(child) ? child.some(check) : check(child);
      };
      const continuous2 = !props.polar && oldChildren.some((child) => {
        var _a;
        return isContinuous(child) || ((_a = child == null ? void 0 : child.props) == null ? void 0 : _a.children) && isContinuous(child.props.children);
      });
      const {
        nodesWillExit,
        nodesWillEnter,
        childrenTransitions,
        nodesShouldEnter
      } = getInitialTransitionState(oldChildren, nextChildren);
      setState({
        nodesWillExit,
        nodesWillEnter,
        nodesShouldEnter,
        childrenTransitions: isArrayOfArrays(childrenTransitions) ? childrenTransitions[0] : childrenTransitions,
        oldProps: nodesWillExit ? props : void 0,
        nextProps,
        continuous: continuous2
      });
    }
  }, [setState]);
  const getProps2 = import_react13.default.useCallback((initialProps) => {
    return state && state.nodesWillExit ? state.oldProps || initialProps : initialProps;
  }, [state]);
  return {
    state,
    setState,
    getAnimationProps,
    setAnimationState,
    getProps: getProps2
  };
};

// node_modules/victory-core/es/victory-util/label-helpers.js
var label_helpers_exports = {};
__export(label_helpers_exports, {
  getDegrees: () => getDegrees,
  getPolarAngle: () => getPolarAngle,
  getPolarTextAnchor: () => getPolarTextAnchor,
  getPolarVerticalAnchor: () => getPolarVerticalAnchor,
  getProps: () => getProps,
  getText: () => getText
});
var import_defaults7 = __toESM(require_defaults());
function getVerticalAnchor(props, datum) {
  if (datum === void 0) {
    datum = {};
  }
  const sign = datum._y >= 0 ? 1 : -1;
  const labelStyle = props.style && props.style.labels || {};
  if (datum.verticalAnchor || labelStyle.verticalAnchor) {
    return datum.verticalAnchor || labelStyle.verticalAnchor;
  } else if (!props.horizontal) {
    return sign >= 0 ? "end" : "start";
  }
  return "middle";
}
function getTextAnchor(props, datum) {
  if (datum === void 0) {
    datum = {};
  }
  const {
    style,
    horizontal
  } = props;
  const sign = datum._y >= 0 ? 1 : -1;
  const labelStyle = style && style.labels || {};
  if (datum.verticalAnchor || labelStyle.verticalAnchor) {
    return datum.verticalAnchor || labelStyle.verticalAnchor;
  } else if (!horizontal) {
    return "middle";
  }
  return sign >= 0 ? "start" : "end";
}
function getAngle(props, datum) {
  if (datum === void 0) {
    datum = {};
  }
  const labelStyle = props.style && props.style.labels || {};
  return datum.angle === void 0 ? labelStyle.angle : datum.angle;
}
function getPadding2(props, datum) {
  if (datum === void 0) {
    datum = {};
  }
  const {
    horizontal,
    style
  } = props;
  const labelStyle = style.labels || {};
  const defaultPadding = evaluateProp(labelStyle.padding, props) || 0;
  const sign = datum._y < 0 ? -1 : 1;
  return {
    x: horizontal ? sign * defaultPadding : 0,
    y: horizontal ? 0 : -1 * sign * defaultPadding
  };
}
function getOffset(props, datum) {
  if (props.polar) {
    return {};
  }
  const padding2 = getPadding2(props, datum);
  return {
    dx: padding2.x,
    dy: padding2.y
  };
}
function getPosition(props, datum) {
  const {
    polar
  } = props;
  const {
    x: x2,
    y: y2
  } = scalePoint(props, datum);
  if (!polar) {
    return {
      x: x2,
      y: y2
    };
  }
  const polarPadding = getPolarPadding(props, datum);
  return {
    x: x2 + polarPadding.x,
    y: y2 + polarPadding.y
  };
}
function getPolarPadding(props, datum) {
  const {
    style
  } = props;
  const degrees = getDegrees(props, datum);
  const labelStyle = style.labels || {};
  const padding2 = evaluateProp(labelStyle.padding, props) || 0;
  const angle = degreesToRadians(degrees);
  return {
    x: padding2 * Math.cos(angle),
    y: -padding2 * Math.sin(angle)
  };
}
function getLabelPlacement(props) {
  const {
    labelComponent,
    labelPlacement,
    polar
  } = props;
  const defaultLabelPlacement = polar ? "perpendicular" : "vertical";
  return labelPlacement ? labelPlacement : labelComponent.props && labelComponent.props.labelPlacement || defaultLabelPlacement;
}
function getPolarOrientation(degrees) {
  if (degrees < 45 || degrees > 315) {
    return "right";
  } else if (degrees >= 45 && degrees <= 135) {
    return "top";
  } else if (degrees > 135 && degrees < 225) {
    return "left";
  }
  return "bottom";
}
function getText(props, datum, index) {
  if (datum === void 0) {
    datum = {};
  }
  if (datum.label !== void 0) {
    return datum.label;
  }
  return Array.isArray(props.labels) ? props.labels[index] : props.labels;
}
function getPolarTextAnchor(props, degrees) {
  const labelPlacement = getLabelPlacement(props);
  if (labelPlacement === "perpendicular" || labelPlacement === "vertical" && (degrees === 90 || degrees === 270)) {
    return "middle";
  }
  return degrees <= 90 || degrees > 270 ? "start" : "end";
}
function getPolarVerticalAnchor(props, degrees) {
  const labelPlacement = getLabelPlacement(props);
  const orientation = getPolarOrientation(degrees);
  if (labelPlacement === "parallel" || orientation === "left" || orientation === "right") {
    return "middle";
  }
  return orientation === "top" ? "end" : "start";
}
function getPolarAngle(props, baseAngle) {
  const {
    labelPlacement,
    datum
  } = props;
  if (!labelPlacement || labelPlacement === "vertical") {
    return 0;
  }
  const degrees = baseAngle !== void 0 ? baseAngle % 360 : getDegrees(props, datum);
  const sign = degrees > 90 && degrees < 180 || degrees > 270 ? 1 : -1;
  let angle = 0;
  if (degrees === 0 || degrees === 180) {
    angle = 90;
  } else if (degrees > 0 && degrees < 180) {
    angle = 90 - degrees;
  } else if (degrees > 180 && degrees < 360) {
    angle = 270 - degrees;
  }
  const labelRotation = labelPlacement === "perpendicular" ? 0 : 90;
  return angle + sign * labelRotation;
}
function getDegrees(props, datum) {
  const {
    x: x2
  } = getPoint(datum);
  return radiansToDegrees(props.scale.x(x2)) % 360;
}
function getProps(props, index) {
  const {
    scale,
    data,
    style,
    horizontal,
    polar,
    width,
    height,
    theme,
    labelComponent,
    disableInlineStyles
  } = props;
  const datum = data[index];
  const degrees = getDegrees(props, datum);
  const textAnchor = polar ? getPolarTextAnchor(props, degrees) : getTextAnchor(props, datum);
  const verticalAnchor = polar ? getPolarVerticalAnchor(props, degrees) : getVerticalAnchor(props, datum);
  const angle = getAngle(props, datum);
  const text = getText(props, datum, index);
  const labelPlacement = getLabelPlacement(props);
  const {
    x: x2,
    y: y2
  } = getPosition(props, datum);
  const {
    dx,
    dy
  } = getOffset(props, datum);
  const labelProps = {
    angle,
    data,
    datum,
    disableInlineStyles,
    horizontal,
    index,
    polar,
    scale,
    labelPlacement,
    text,
    textAnchor,
    verticalAnchor,
    x: x2,
    y: y2,
    dx,
    dy,
    width,
    height,
    style: style.labels
  };
  if (!isTooltip(labelComponent)) {
    return labelProps;
  }
  const tooltipTheme = theme && theme.tooltip || {};
  return (0, import_defaults7.default)({}, labelProps, omit(tooltipTheme, ["style"]));
}

// node_modules/victory-core/es/victory-util/line-helpers.js
var line_helpers_exports = {};
__export(line_helpers_exports, {
  getInterpolationFunction: () => getInterpolationFunction,
  getLineFunction: () => getLineFunction
});

// node_modules/victory-core/node_modules/victory-vendor/es/d3-shape.js
var d3_shape_exports = {};
__export(d3_shape_exports, {
  arc: () => arc_default,
  area: () => area_default,
  areaRadial: () => areaRadial_default,
  curveBasis: () => basis_default,
  curveBasisClosed: () => basisClosed_default,
  curveBasisOpen: () => basisOpen_default,
  curveBumpX: () => bumpX,
  curveBumpY: () => bumpY,
  curveBundle: () => bundle_default,
  curveCardinal: () => cardinal_default,
  curveCardinalClosed: () => cardinalClosed_default,
  curveCardinalOpen: () => cardinalOpen_default,
  curveCatmullRom: () => catmullRom_default,
  curveCatmullRomClosed: () => catmullRomClosed_default,
  curveCatmullRomOpen: () => catmullRomOpen_default,
  curveLinear: () => linear_default,
  curveLinearClosed: () => linearClosed_default,
  curveMonotoneX: () => monotoneX,
  curveMonotoneY: () => monotoneY,
  curveNatural: () => natural_default,
  curveStep: () => step_default,
  curveStepAfter: () => stepAfter,
  curveStepBefore: () => stepBefore,
  line: () => line_default,
  lineRadial: () => lineRadial_default,
  link: () => link,
  linkHorizontal: () => linkHorizontal,
  linkRadial: () => linkRadial,
  linkVertical: () => linkVertical,
  pie: () => pie_default,
  pointRadial: () => pointRadial_default,
  radialArea: () => areaRadial_default,
  radialLine: () => lineRadial_default,
  stack: () => stack_default,
  stackOffsetDiverging: () => diverging_default,
  stackOffsetExpand: () => expand_default,
  stackOffsetNone: () => none_default,
  stackOffsetSilhouette: () => silhouette_default,
  stackOffsetWiggle: () => wiggle_default,
  stackOrderAppearance: () => appearance_default,
  stackOrderAscending: () => ascending_default,
  stackOrderDescending: () => descending_default,
  stackOrderInsideOut: () => insideOut_default,
  stackOrderNone: () => none_default2,
  stackOrderReverse: () => reverse_default,
  symbol: () => Symbol2,
  symbolAsterisk: () => asterisk_default,
  symbolCircle: () => circle_default,
  symbolCross: () => cross_default,
  symbolDiamond: () => diamond_default,
  symbolDiamond2: () => diamond2_default,
  symbolPlus: () => plus_default,
  symbolSquare: () => square_default,
  symbolSquare2: () => square2_default,
  symbolStar: () => star_default,
  symbolTimes: () => times_default,
  symbolTriangle: () => triangle_default,
  symbolTriangle2: () => triangle2_default,
  symbolWye: () => wye_default,
  symbolX: () => times_default,
  symbols: () => symbolsFill,
  symbolsFill: () => symbolsFill,
  symbolsStroke: () => symbolsStroke
});

// node_modules/victory-core/es/victory-util/line-helpers.js
var defined = (d) => {
  const y2 = d._y1 !== void 0 ? d._y1 : d._y;
  return y2 !== null && y2 !== void 0 && d._y0 !== null;
};
var getXAccessor = (scale) => {
  return (d) => scale.x(d._x1 !== void 0 ? d._x1 : d._x);
};
var getYAccessor = (scale) => {
  return (d) => scale.y(d._y1 !== void 0 ? d._y1 : d._y);
};
var getAngleAccessor = (scale) => {
  return (d) => {
    const x2 = scale.x(d._x1 !== void 0 ? d._x1 : d._x);
    return -1 * x2 + Math.PI / 2;
  };
};
var toNewName2 = (interpolation) => {
  const capitalize = (s) => s && s[0].toUpperCase() + s.slice(1);
  return `curve${capitalize(interpolation)}`;
};
var toNewNameClosed = (interpolation) => {
  return `${toNewName2(interpolation)}Closed`;
};
var getInterpolationFunction = (props) => {
  const {
    interpolation
  } = props;
  if (typeof interpolation === "function") {
    return interpolation;
  }
  if (typeof interpolation === "string") {
    const {
      polar,
      openCurve = !polar
    } = props;
    const interpolationName = !openCurve ? toNewNameClosed(interpolation) : toNewName2(interpolation);
    return d3_shape_exports[interpolationName];
  }
  return linear_default;
};
var getLineFunction = (props) => {
  const {
    polar,
    scale,
    horizontal
  } = props;
  return polar ? lineRadial_default().defined(defined).curve(getInterpolationFunction(props)).angle(getAngleAccessor(scale)).radius(getYAccessor(scale)) : line_default().defined(defined).curve(getInterpolationFunction(props)).x(horizontal ? getYAccessor(scale) : getXAccessor(scale)).y(horizontal ? getXAccessor(scale) : getYAccessor(scale));
};

// node_modules/victory-core/es/victory-util/log.js
var log_exports = {};
__export(log_exports, {
  warn: () => warn
});
function warn(message) {
  if (true) {
    if (console && console.warn) {
      console.warn(message);
    }
  }
}

// node_modules/victory-core/es/victory-util/point-path-helpers.js
var point_path_helpers_exports = {};
__export(point_path_helpers_exports, {
  circle: () => circle,
  cross: () => cross,
  diamond: () => diamond,
  minus: () => minus,
  plus: () => plus,
  square: () => square2,
  star: () => star,
  triangleDown: () => triangleDown,
  triangleUp: () => triangleUp
});
function circle(x2, y2, size) {
  return `M ${x2}, ${y2}
      m ${-size}, 0
      a ${size}, ${size} 0 1,0 ${size * 2},0
      a ${size}, ${size} 0 1,0 ${-size * 2},0`;
}
function square2(x2, y2, size) {
  const baseSize = 0.87 * size;
  const x0 = x2 - baseSize;
  const y1 = y2 + baseSize;
  const distance = x2 + baseSize - x0;
  return `M ${x0}, ${y1}
      h${distance}
      v-${distance}
      h-${distance}
      z`;
}
function diamond(x2, y2, size) {
  const baseSize = 0.87 * size;
  const length = Math.sqrt(2 * (baseSize * baseSize));
  return `M ${x2}, ${y2 + length}
      l ${length}, -${length}
      l -${length}, -${length}
      l -${length}, ${length}
      l ${length}, ${length}
      z`;
}
function triangleDown(x2, y2, size) {
  const height = size / 2 * Math.sqrt(3);
  const x0 = x2 - size;
  const x1 = x2 + size;
  const y0 = y2 - size;
  const y1 = y2 + height;
  return `M ${x0}, ${y0}
      L ${x1}, ${y0}
      L ${x2}, ${y1}
      z`;
}
function triangleUp(x2, y2, size) {
  const height = size / 2 * Math.sqrt(3);
  const x0 = x2 - size;
  const x1 = x2 + size;
  const y0 = y2 - height;
  const y1 = y2 + size;
  return `M ${x0}, ${y1}
      L ${x1}, ${y1}
      L ${x2}, ${y0}
      z`;
}
function plus(x2, y2, size) {
  const baseSize = 1.1 * size;
  const distance = baseSize / 1.5;
  return `
      M ${x2 - distance / 2}, ${y2 + baseSize}
      v-${distance}
      h-${distance}
      v-${distance}
      h${distance}
      v-${distance}
      h${distance}
      v${distance}
      h${distance}
      v${distance}
      h-${distance}
      v${distance}
      z`;
}
function cross(x2, y2, size) {
  const baseSize = 0.8 * size;
  const distance = baseSize / 1.5;
  return `
      M ${x2 - distance / 2}, ${y2 + baseSize + distance}
      v-${distance * 2}
      h-${distance}
      v-${distance}
      h${distance}
      v-${distance}
      h${distance}
      v${distance}
      h${distance}
      v${distance}
      h-${distance}
      v${distance * 2}
      z`;
}
function minus(x2, y2, size) {
  const baseSize = 1.1 * size;
  const lineHeight = baseSize - baseSize * 0.3;
  const x0 = x2 - baseSize;
  const y1 = y2 + lineHeight / 2;
  const distance = x2 + baseSize - x0;
  return `M ${x0}, ${y1}
      h${distance}
      v-${lineHeight}
      h-${distance}
      z`;
}
function star(x2, y2, size) {
  const baseSize = 1.35 * size;
  const angle = Math.PI / 5;
  const starCoords = range2(10).map((index) => {
    const length = index % 2 === 0 ? baseSize : baseSize / 2;
    return `${length * Math.sin(angle * (index + 1)) + x2},
        ${length * Math.cos(angle * (index + 1)) + y2}`;
  });
  return `M ${starCoords.join("L")} z`;
}

// node_modules/victory-core/es/victory-util/selection.js
var selection_exports = {};
__export(selection_exports, {
  getBounds: () => getBounds,
  getDataCoordinates: () => getDataCoordinates,
  getDomainCoordinates: () => getDomainCoordinates,
  getParentSVG: () => getParentSVG,
  getSVGEventCoordinates: () => getSVGEventCoordinates
});
function transformTarget(target, matrix, dimension) {
  const {
    a,
    d,
    e,
    f
  } = matrix;
  return dimension === "y" ? d * target + f : a * target + e;
}
function getTransformationMatrix(svg) {
  return svg.getScreenCTM().inverse();
}
function isNativeTouchEvent(nativeEvent) {
  return !!(nativeEvent && nativeEvent.identifier !== void 0);
}
function isReactTouchEvent(evt) {
  return evt.changedTouches && evt.changedTouches.length > 0;
}
function getParentSVG(evt) {
  if (isNativeTouchEvent(evt.nativeEvent)) {
    return void 0;
  }
  const getParent = (target) => {
    if (target.nodeName === "svg") {
      return target;
    }
    return target.parentNode ? getParent(target.parentNode) : target;
  };
  return getParent(evt.target);
}
function getSVGEventCoordinates(evt, svg) {
  if (isNativeTouchEvent(evt.nativeEvent)) {
    return {
      x: evt.nativeEvent.locationX,
      y: evt.nativeEvent.locationY
    };
  }
  const location = isReactTouchEvent(evt) ? evt.changedTouches[0] : evt;
  const matrix = getTransformationMatrix(svg || getParentSVG(location));
  return {
    x: transformTarget(location.clientX, matrix, "x"),
    y: transformTarget(location.clientY, matrix, "y")
  };
}
function getDomainCoordinates(props, domain) {
  const {
    horizontal
  } = props;
  const scale = props.scale;
  const domainObj = domain || {
    x: scale.x.domain(),
    y: scale.y.domain()
  };
  return {
    x: horizontal ? [scale.y(domainObj.y[0]), scale.y(domainObj.y[1])] : [scale.x(domainObj.x[0]), scale.x(domainObj.x[1])],
    y: horizontal ? [scale.x(domainObj.x[0]), scale.x(domainObj.x[1])] : [scale.y(domainObj.y[0]), scale.y(domainObj.y[1])]
  };
}
function getDataCoordinates(props, scale, x2, y2) {
  const {
    polar,
    horizontal
  } = props;
  if (!polar) {
    return {
      x: horizontal ? scale.x.invert(y2) : scale.x.invert(x2),
      y: horizontal ? scale.y.invert(x2) : scale.y.invert(y2)
    };
  }
  const origin = props.origin || {
    x: 0,
    y: 0
  };
  const baseX = x2 - origin.x;
  const baseY = y2 - origin.y;
  const radius = Math.abs(baseX * Math.sqrt(1 + Math.pow(-baseY / baseX, 2)));
  const angle = (-Math.atan2(baseY, baseX) + Math.PI * 2) % (Math.PI * 2);
  return {
    x: scale.x.invert(angle),
    y: scale.y.invert(radius)
  };
}
function getBounds(props) {
  const {
    x1,
    x2,
    y1,
    y2,
    scale
  } = props;
  const point1 = getDataCoordinates(props, scale, x1, y1);
  const point22 = getDataCoordinates(props, scale, x2, y2);
  const makeBound = (a, b) => {
    return [getMinValue([a, b]), getMaxValue([a, b])];
  };
  return {
    x: makeBound(point1.x, point22.x),
    y: makeBound(point1.y, point22.y)
  };
}

// node_modules/victory-core/es/victory-util/style.js
var style_exports = {};
__export(style_exports, {
  getColorScale: () => getColorScale,
  toTransformString: () => toTransformString
});
var toTransformString = function(obj) {
  for (var _len = arguments.length, more = new Array(_len > 1 ? _len - 1 : 0), _key = 1; _key < _len; _key++) {
    more[_key - 1] = arguments[_key];
  }
  if (more.length > 0) {
    return more.reduce((memo, currentObj) => {
      return [memo, toTransformString(currentObj)].join(" ");
    }, toTransformString(obj)).trim();
  }
  if (obj === void 0 || obj === null || typeof obj === "string") {
    return obj;
  }
  const transforms = [];
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      const value = obj[key];
      transforms.push(`${key}(${value})`);
    }
  }
  return transforms.join(" ").trim();
};
function getColorScale(name) {
  const scales = {
    grayscale: ["#cccccc", "#969696", "#636363", "#252525"],
    qualitative: ["#334D5C", "#45B29D", "#EFC94C", "#E27A3F", "#DF5A49", "#4F7DA1", "#55DBC1", "#EFDA97", "#E2A37F", "#DF948A"],
    heatmap: ["#428517", "#77D200", "#D6D305", "#EC8E19", "#C92B05"],
    warm: ["#940031", "#C43343", "#DC5429", "#FF821D", "#FFAF55"],
    cool: ["#2746B9", "#0B69D4", "#2794DB", "#31BB76", "#60E83B"],
    red: ["#FCAE91", "#FB6A4A", "#DE2D26", "#A50F15", "#750B0E"],
    blue: ["#002C61", "#004B8F", "#006BC9", "#3795E5", "#65B4F4"],
    green: ["#354722", "#466631", "#649146", "#8AB25C", "#A9C97E"]
  };
  return name ? scales[name] : scales.grayscale;
}

// node_modules/victory-core/es/victory-util/textsize.js
var textsize_exports = {};
__export(textsize_exports, {
  _approximateTextSizeInternal: () => _approximateTextSizeInternal,
  approximateTextSize: () => approximateTextSize,
  convertLengthToPixels: () => convertLengthToPixels
});
var import_memoize = __toESM(require_memoize());
var import_defaults8 = __toESM(require_defaults());
var fonts = {
  "American Typewriter": {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.25, 0.4203125, 0.3296875, 0.6, 0.6375, 0.8015625, 0.8203125, 0.1875, 0.45625, 0.45625, 0.6375, 0.5, 0.2734375, 0.309375, 0.2734375, 0.4390625, 0.6375, 0.6375, 0.6375, 0.6375, 0.6375, 0.6375, 0.6375, 0.6375, 0.6375, 0.6375, 0.2734375, 0.2734375, 0.5, 0.5, 0.5, 0.6, 0.6921875, 0.7640625, 0.6921875, 0.6375, 0.728125, 0.6734375, 0.6203125, 0.7109375, 0.784375, 0.3828125, 0.6421875, 0.7859375, 0.6375, 0.9484375, 0.7640625, 0.65625, 0.6375, 0.65625, 0.7296875, 0.6203125, 0.6375, 0.7109375, 0.740625, 0.940625, 0.784375, 0.7578125, 0.6203125, 0.4375, 0.5, 0.4375, 0.5, 0.5, 0.4921875, 0.5734375, 0.5890625, 0.5109375, 0.6, 0.528125, 0.43125, 0.5578125, 0.6375, 0.3109375, 0.40625, 0.6234375, 0.309375, 0.928125, 0.6375, 0.546875, 0.6, 0.58125, 0.4921875, 0.4921875, 0.4, 0.6203125, 0.625, 0.825, 0.6375, 0.640625, 0.528125, 0.5, 0.5, 0.5, 0.6671875],
    avg: 0.5793421052631578
  },
  Arial: {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.278125, 0.278125, 0.35625, 0.55625, 0.55625, 0.890625, 0.6671875, 0.1921875, 0.334375, 0.334375, 0.390625, 0.584375, 0.278125, 0.334375, 0.278125, 0.278125, 0.55625, 0.55625, 0.55625, 0.55625, 0.55625, 0.55625, 0.55625, 0.55625, 0.55625, 0.55625, 0.278125, 0.278125, 0.584375, 0.584375, 0.584375, 0.55625, 1.015625, 0.6703125, 0.6671875, 0.7234375, 0.7234375, 0.6671875, 0.6109375, 0.778125, 0.7234375, 0.278125, 0.5, 0.6671875, 0.55625, 0.834375, 0.7234375, 0.778125, 0.6671875, 0.778125, 0.7234375, 0.6671875, 0.6109375, 0.7234375, 0.6671875, 0.9453125, 0.6671875, 0.6671875, 0.6109375, 0.278125, 0.278125, 0.278125, 0.4703125, 0.584375, 0.334375, 0.55625, 0.55625, 0.5, 0.55625, 0.55625, 0.3125, 0.55625, 0.55625, 0.2234375, 0.2703125, 0.5, 0.2234375, 0.834375, 0.55625, 0.55625, 0.55625, 0.55625, 0.346875, 0.5, 0.278125, 0.55625, 0.5, 0.7234375, 0.5, 0.5, 0.5, 0.334375, 0.2609375, 0.334375, 0.584375],
    avg: 0.528733552631579
  },
  "Arial Black": {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.33125, 0.334375, 0.5, 0.6609375, 0.6671875, 1, 0.890625, 0.278125, 0.390625, 0.390625, 0.55625, 0.6609375, 0.334375, 0.334375, 0.334375, 0.28125, 0.6671875, 0.6671875, 0.6671875, 0.6671875, 0.6671875, 0.6671875, 0.6671875, 0.6671875, 0.6671875, 0.6671875, 0.334375, 0.334375, 0.6609375, 0.6609375, 0.6609375, 0.6109375, 0.7453125, 0.78125, 0.778125, 0.778125, 0.778125, 0.7234375, 0.6671875, 0.834375, 0.834375, 0.390625, 0.6671875, 0.834375, 0.6671875, 0.9453125, 0.834375, 0.834375, 0.7234375, 0.834375, 0.78125, 0.7234375, 0.7234375, 0.834375, 0.7796875, 1.003125, 0.78125, 0.78125, 0.7234375, 0.390625, 0.28125, 0.390625, 0.6609375, 0.5125, 0.334375, 0.6671875, 0.6671875, 0.6671875, 0.6671875, 0.6671875, 0.41875, 0.6671875, 0.6671875, 0.334375, 0.384375, 0.6671875, 0.334375, 1, 0.6671875, 0.6671875, 0.6671875, 0.6671875, 0.4703125, 0.6109375, 0.4453125, 0.6671875, 0.6140625, 0.946875, 0.6671875, 0.615625, 0.55625, 0.390625, 0.278125, 0.390625, 0.6609375],
    avg: 0.6213157894736842
  },
  Baskerville: {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.25, 0.25, 0.40625, 0.6671875, 0.490625, 0.875, 0.7015625, 0.178125, 0.2453125, 0.246875, 0.4171875, 0.6671875, 0.25, 0.3125, 0.25, 0.521875, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.25, 0.25, 0.6671875, 0.6671875, 0.6671875, 0.396875, 0.9171875, 0.684375, 0.615625, 0.71875, 0.7609375, 0.625, 0.553125, 0.771875, 0.803125, 0.3546875, 0.515625, 0.78125, 0.6046875, 0.928125, 0.75, 0.8234375, 0.5625, 0.96875, 0.7296875, 0.5421875, 0.6984375, 0.771875, 0.7296875, 0.9484375, 0.771875, 0.678125, 0.6359375, 0.3640625, 0.521875, 0.3640625, 0.46875, 0.5125, 0.334375, 0.46875, 0.521875, 0.428125, 0.521875, 0.4375, 0.3890625, 0.4765625, 0.53125, 0.25, 0.359375, 0.4640625, 0.240625, 0.803125, 0.53125, 0.5, 0.521875, 0.521875, 0.365625, 0.334375, 0.2921875, 0.521875, 0.4640625, 0.678125, 0.4796875, 0.465625, 0.428125, 0.4796875, 0.5109375, 0.4796875, 0.6671875],
    avg: 0.5323519736842108
  },
  Courier: {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5984375, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6078125, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.61875, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.615625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6140625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625],
    avg: 0.6020559210526316
  },
  "Courier New": {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5984375, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625],
    avg: 0.6015296052631579
  },
  cursive: {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.1921875, 0.24375, 0.40625, 0.5671875, 0.3984375, 0.721875, 0.909375, 0.2328125, 0.434375, 0.365625, 0.4734375, 0.5578125, 0.19375, 0.3484375, 0.19375, 0.7734375, 0.503125, 0.4171875, 0.5453125, 0.45, 0.6046875, 0.4703125, 0.5984375, 0.55625, 0.503125, 0.5546875, 0.20625, 0.2, 0.5625, 0.5546875, 0.546875, 0.403125, 0.70625, 0.734375, 0.7078125, 0.64375, 0.85, 0.753125, 0.75, 0.6484375, 1.0765625, 0.44375, 0.5359375, 0.8359375, 0.653125, 1.0109375, 1.1515625, 0.6796875, 0.6984375, 1.0625, 0.8234375, 0.5125, 0.9234375, 0.8546875, 0.70625, 0.9109375, 0.7421875, 0.715625, 0.6015625, 0.4640625, 0.3359375, 0.4109375, 0.5421875, 0.5421875, 0.4328125, 0.5125, 0.5, 0.3859375, 0.7375, 0.359375, 0.75625, 0.540625, 0.5328125, 0.3203125, 0.5296875, 0.5015625, 0.484375, 0.7890625, 0.5640625, 0.4203125, 0.703125, 0.471875, 0.4734375, 0.35, 0.4125, 0.5640625, 0.471875, 0.6484375, 0.5296875, 0.575, 0.4140625, 0.415625, 0.20625, 0.3796875, 0.5421875],
    avg: 0.5604440789473684
  },
  fantasy: {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.215625, 0.2625, 0.3265625, 0.6109375, 0.534375, 0.7625, 0.7828125, 0.2, 0.4359375, 0.4359375, 0.3765625, 0.5109375, 0.2796875, 0.4609375, 0.2796875, 0.5296875, 0.6640625, 0.253125, 0.521875, 0.4765625, 0.6640625, 0.490625, 0.528125, 0.5546875, 0.496875, 0.5421875, 0.2796875, 0.2796875, 0.5625, 0.4609375, 0.5625, 0.4828125, 0.609375, 0.740625, 0.7234375, 0.740625, 0.8265625, 0.7234375, 0.6171875, 0.7359375, 0.765625, 0.240625, 0.5453125, 0.715625, 0.6078125, 0.8640625, 0.653125, 0.9125, 0.6484375, 0.946875, 0.6921875, 0.653125, 0.6953125, 0.8015625, 0.58125, 0.784375, 0.671875, 0.6265625, 0.690625, 0.4359375, 0.5296875, 0.4359375, 0.53125, 0.5, 0.2875, 0.5375, 0.603125, 0.4984375, 0.60625, 0.53125, 0.434375, 0.6421875, 0.56875, 0.209375, 0.4671875, 0.5484375, 0.2203125, 0.709375, 0.55, 0.5984375, 0.6140625, 0.5765625, 0.40625, 0.4734375, 0.3734375, 0.559375, 0.4421875, 0.6421875, 0.4890625, 0.578125, 0.4484375, 0.2546875, 0.2203125, 0.2546875, 0.55],
    avg: 0.536496710526316
  },
  Geneva: {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.3328125, 0.3046875, 0.5, 0.6671875, 0.6671875, 0.90625, 0.728125, 0.3046875, 0.446875, 0.446875, 0.5078125, 0.6671875, 0.3046875, 0.3796875, 0.3046875, 0.5390625, 0.6671875, 0.6671875, 0.6671875, 0.6671875, 0.6671875, 0.6671875, 0.6671875, 0.6671875, 0.6671875, 0.6671875, 0.3046875, 0.3046875, 0.6671875, 0.6671875, 0.6671875, 0.56875, 0.871875, 0.728125, 0.6375, 0.6515625, 0.7015625, 0.5765625, 0.5546875, 0.675, 0.690625, 0.2421875, 0.4921875, 0.6640625, 0.584375, 0.7890625, 0.709375, 0.7359375, 0.584375, 0.78125, 0.60625, 0.60625, 0.640625, 0.6671875, 0.728125, 0.946875, 0.6109375, 0.6109375, 0.5765625, 0.446875, 0.5390625, 0.446875, 0.6671875, 0.6671875, 0.5921875, 0.5546875, 0.6109375, 0.546875, 0.603125, 0.5765625, 0.390625, 0.6109375, 0.584375, 0.2359375, 0.334375, 0.5390625, 0.2359375, 0.8953125, 0.584375, 0.60625, 0.603125, 0.603125, 0.3875, 0.509375, 0.44375, 0.584375, 0.565625, 0.78125, 0.53125, 0.571875, 0.5546875, 0.4515625, 0.246875, 0.4515625, 0.6671875],
    avg: 0.5762664473684211
  },
  Georgia: {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.2421875, 0.33125, 0.4125, 0.64375, 0.6109375, 0.81875, 0.7109375, 0.215625, 0.375, 0.375, 0.4734375, 0.64375, 0.2703125, 0.375, 0.2703125, 0.46875, 0.6140625, 0.4296875, 0.559375, 0.553125, 0.565625, 0.5296875, 0.5671875, 0.503125, 0.596875, 0.5671875, 0.3125, 0.3125, 0.64375, 0.64375, 0.64375, 0.4796875, 0.9296875, 0.715625, 0.6546875, 0.6421875, 0.75, 0.6546875, 0.6, 0.7265625, 0.815625, 0.390625, 0.51875, 0.7203125, 0.6046875, 0.928125, 0.7671875, 0.7453125, 0.6109375, 0.7453125, 0.7234375, 0.5625, 0.61875, 0.7578125, 0.70625, 0.99375, 0.7125, 0.6640625, 0.6015625, 0.375, 0.46875, 0.375, 0.64375, 0.65, 0.5, 0.5046875, 0.56875, 0.4546875, 0.575, 0.484375, 0.39375, 0.509375, 0.5828125, 0.29375, 0.3671875, 0.546875, 0.2875, 0.88125, 0.5921875, 0.5390625, 0.571875, 0.5640625, 0.4109375, 0.4328125, 0.3453125, 0.5765625, 0.5203125, 0.75625, 0.50625, 0.5171875, 0.4453125, 0.43125, 0.375, 0.43125, 0.64375],
    avg: 0.5551809210526316
  },
  "Gill Sans": {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.2765625, 0.271875, 0.3546875, 0.584375, 0.5421875, 0.6765625, 0.625, 0.1890625, 0.3234375, 0.3234375, 0.4171875, 0.584375, 0.2203125, 0.3234375, 0.2203125, 0.28125, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.2203125, 0.2296875, 0.584375, 0.584375, 0.584375, 0.334375, 1.0109375, 0.6671875, 0.5640625, 0.709375, 0.75, 0.5, 0.4703125, 0.740625, 0.7296875, 0.25, 0.3125, 0.65625, 0.490625, 0.78125, 0.78125, 0.8234375, 0.5109375, 0.8234375, 0.6046875, 0.459375, 0.6046875, 0.709375, 0.6046875, 1.0421875, 0.709375, 0.6046875, 0.646875, 0.334375, 0.28125, 0.334375, 0.4703125, 0.5828125, 0.334375, 0.428125, 0.5, 0.4390625, 0.5109375, 0.4796875, 0.296875, 0.428125, 0.5, 0.2203125, 0.2265625, 0.5, 0.2203125, 0.771875, 0.5, 0.553125, 0.5, 0.5, 0.3984375, 0.3859375, 0.334375, 0.5, 0.4390625, 0.7203125, 0.5, 0.4390625, 0.4171875, 0.334375, 0.2609375, 0.334375, 0.584375],
    avg: 0.4933717105263159
  },
  Helvetica: {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.2796875, 0.2765625, 0.3546875, 0.5546875, 0.5546875, 0.8890625, 0.665625, 0.190625, 0.3328125, 0.3328125, 0.3890625, 0.5828125, 0.2765625, 0.3328125, 0.2765625, 0.3015625, 0.5546875, 0.5546875, 0.5546875, 0.5546875, 0.5546875, 0.5546875, 0.5546875, 0.5546875, 0.5546875, 0.5546875, 0.2765625, 0.2765625, 0.584375, 0.5828125, 0.584375, 0.5546875, 1.0140625, 0.665625, 0.665625, 0.721875, 0.721875, 0.665625, 0.609375, 0.7765625, 0.721875, 0.2765625, 0.5, 0.665625, 0.5546875, 0.8328125, 0.721875, 0.7765625, 0.665625, 0.7765625, 0.721875, 0.665625, 0.609375, 0.721875, 0.665625, 0.94375, 0.665625, 0.665625, 0.609375, 0.2765625, 0.3546875, 0.2765625, 0.4765625, 0.5546875, 0.3328125, 0.5546875, 0.5546875, 0.5, 0.5546875, 0.5546875, 0.2765625, 0.5546875, 0.5546875, 0.221875, 0.240625, 0.5, 0.221875, 0.8328125, 0.5546875, 0.5546875, 0.5546875, 0.5546875, 0.3328125, 0.5, 0.2765625, 0.5546875, 0.5, 0.721875, 0.5, 0.5, 0.5, 0.3546875, 0.259375, 0.353125, 0.5890625],
    avg: 0.5279276315789471
  },
  "Helvetica Neue": {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.278125, 0.259375, 0.4265625, 0.55625, 0.55625, 1, 0.6453125, 0.278125, 0.2703125, 0.26875, 0.353125, 0.6, 0.278125, 0.3890625, 0.278125, 0.36875, 0.55625, 0.55625, 0.55625, 0.55625, 0.55625, 0.55625, 0.55625, 0.55625, 0.55625, 0.55625, 0.278125, 0.278125, 0.6, 0.6, 0.6, 0.55625, 0.8, 0.6625, 0.6859375, 0.7234375, 0.7046875, 0.6125, 0.575, 0.759375, 0.7234375, 0.259375, 0.5203125, 0.6703125, 0.55625, 0.871875, 0.7234375, 0.7609375, 0.6484375, 0.7609375, 0.6859375, 0.6484375, 0.575, 0.7234375, 0.6140625, 0.9265625, 0.6125, 0.6484375, 0.6125, 0.259375, 0.36875, 0.259375, 0.6, 0.5, 0.25625, 0.5375, 0.59375, 0.5375, 0.59375, 0.5375, 0.2984375, 0.575, 0.55625, 0.2234375, 0.2375, 0.5203125, 0.2234375, 0.853125, 0.55625, 0.575, 0.59375, 0.59375, 0.334375, 0.5, 0.315625, 0.55625, 0.5, 0.759375, 0.51875, 0.5, 0.48125, 0.334375, 0.2234375, 0.334375, 0.6],
    avg: 0.5279440789473684
  },
  "Hoefler Text": {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.2359375, 0.2234375, 0.3921875, 0.7125, 0.49375, 0.8859375, 0.771875, 0.2125, 0.3078125, 0.309375, 0.375, 0.4234375, 0.234375, 0.3125, 0.234375, 0.3, 0.5828125, 0.365625, 0.434375, 0.3921875, 0.5234375, 0.3984375, 0.5125, 0.4328125, 0.46875, 0.5125, 0.234375, 0.234375, 0.515625, 0.4234375, 0.515625, 0.340625, 0.7609375, 0.7359375, 0.6359375, 0.721875, 0.8125, 0.6375, 0.5875, 0.8078125, 0.853125, 0.4296875, 0.503125, 0.78125, 0.609375, 0.9609375, 0.8515625, 0.8140625, 0.6125, 0.8140625, 0.71875, 0.49375, 0.7125, 0.76875, 0.771875, 1.125, 0.7765625, 0.7734375, 0.65625, 0.321875, 0.3078125, 0.321875, 0.3546875, 0.5, 0.3375, 0.446875, 0.5359375, 0.45, 0.5296875, 0.4546875, 0.425, 0.4921875, 0.54375, 0.2671875, 0.240625, 0.5390625, 0.25, 0.815625, 0.5375, 0.5234375, 0.5390625, 0.5421875, 0.365625, 0.36875, 0.35625, 0.5171875, 0.5015625, 0.75, 0.5, 0.509375, 0.44375, 0.2421875, 0.14375, 0.2421875, 0.35],
    avg: 0.5116447368421051
  },
  "Montserrat": {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.2625, 0.2609375, 0.3734375, 0.696875, 0.615625, 0.8296875, 0.6703125, 0.203125, 0.3296875, 0.3296875, 0.3875, 0.575, 0.2125, 0.3828125, 0.2125, 0.3953125, 0.6625, 0.3625, 0.56875, 0.5640625, 0.6625, 0.5671875, 0.609375, 0.5890625, 0.6390625, 0.609375, 0.2125, 0.2125, 0.575, 0.575, 0.575, 0.5671875, 1.034375, 0.7171875, 0.7546875, 0.7203125, 0.8265625, 0.6703125, 0.634375, 0.7734375, 0.8140625, 0.303125, 0.5078125, 0.7125, 0.5890625, 0.95625, 0.8140625, 0.8390625, 0.71875, 0.8390625, 0.7234375, 0.615625, 0.575, 0.7921875, 0.6984375, 1.1125, 0.65625, 0.6359375, 0.6515625, 0.31875, 0.396875, 0.31875, 0.5765625, 0.5, 0.6, 0.590625, 0.678125, 0.5640625, 0.678125, 0.6046875, 0.375, 0.6875, 0.678125, 0.2703125, 0.365625, 0.6015625, 0.2703125, 1.0625, 0.678125, 0.628125, 0.678125, 0.678125, 0.4015625, 0.4890625, 0.40625, 0.6734375, 0.5421875, 0.8796875, 0.534375, 0.5671875, 0.5125, 0.334375, 0.2953125, 0.334375, 0.575],
    avg: 0.571792763157895
  },
  monospace: {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5984375, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6078125, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.61875, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.615625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6140625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625, 0.6015625],
    avg: 0.6020559210526316
  },
  Overpass: {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.2296875, 0.2765625, 0.4203125, 0.68125, 0.584375, 0.8515625, 0.7015625, 0.2203125, 0.3453125, 0.3453125, 0.53125, 0.63125, 0.2234375, 0.3953125, 0.2234375, 0.509375, 0.65, 0.4046875, 0.6171875, 0.60625, 0.6484375, 0.60625, 0.6015625, 0.5375, 0.615625, 0.6015625, 0.2234375, 0.2234375, 0.63125, 0.63125, 0.63125, 0.5015625, 0.8203125, 0.696875, 0.6671875, 0.65, 0.6859375, 0.6015625, 0.559375, 0.690625, 0.7078125, 0.2953125, 0.565625, 0.678125, 0.58125, 0.8046875, 0.7109375, 0.740625, 0.6421875, 0.740625, 0.6765625, 0.6046875, 0.590625, 0.696875, 0.6640625, 0.853125, 0.65, 0.6671875, 0.6625, 0.3734375, 0.509375, 0.3734375, 0.63125, 0.5125, 0.4, 0.5328125, 0.5625, 0.51875, 0.5625, 0.546875, 0.3359375, 0.5625, 0.565625, 0.25625, 0.3203125, 0.55, 0.265625, 0.85, 0.565625, 0.5671875, 0.5625, 0.5625, 0.4046875, 0.4765625, 0.3796875, 0.565625, 0.521875, 0.7265625, 0.53125, 0.5390625, 0.5125, 0.3671875, 0.275, 0.3671875, 0.63125],
    avg: 0.5430756578947369
  },
  Palatino: {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.25, 0.278125, 0.371875, 0.60625, 0.5, 0.840625, 0.778125, 0.209375, 0.334375, 0.334375, 0.390625, 0.60625, 0.2578125, 0.334375, 0.25, 0.60625, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.25, 0.25, 0.60625, 0.60625, 0.60625, 0.4453125, 0.7484375, 0.778125, 0.6109375, 0.709375, 0.775, 0.6109375, 0.55625, 0.7640625, 0.8328125, 0.3375, 0.346875, 0.7265625, 0.6109375, 0.946875, 0.83125, 0.7875, 0.6046875, 0.7875, 0.66875, 0.525, 0.6140625, 0.778125, 0.7234375, 1, 0.6671875, 0.6671875, 0.6671875, 0.334375, 0.60625, 0.334375, 0.60625, 0.5, 0.334375, 0.5, 0.565625, 0.4453125, 0.6109375, 0.4796875, 0.340625, 0.55625, 0.5828125, 0.2921875, 0.2671875, 0.5640625, 0.2921875, 0.8828125, 0.5828125, 0.546875, 0.6015625, 0.5609375, 0.3953125, 0.425, 0.3265625, 0.603125, 0.565625, 0.834375, 0.5171875, 0.55625, 0.5, 0.334375, 0.60625, 0.334375, 0.60625],
    avg: 0.5408552631578947
  },
  "RedHatText": {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.2328125, 0.2203125, 0.35625, 0.6890625, 0.55, 0.7390625, 0.6703125, 0.2140625, 0.4015625, 0.4015625, 0.4546875, 0.53125, 0.2203125, 0.45625, 0.2203125, 0.515625, 0.6609375, 0.3078125, 0.5484375, 0.5875, 0.61875, 0.5703125, 0.6203125, 0.559375, 0.6140625, 0.6203125, 0.2203125, 0.2234375, 0.465625, 0.534375, 0.465625, 0.5125, 0.7671875, 0.6609375, 0.6703125, 0.7265625, 0.728125, 0.6203125, 0.6109375, 0.8, 0.73125, 0.253125, 0.6, 0.6125, 0.6078125, 0.8625, 0.7390625, 0.8109375, 0.6546875, 0.809375, 0.6484375, 0.6234375, 0.6171875, 0.7125, 0.6609375, 0.8984375, 0.6546875, 0.646875, 0.60625, 0.3625, 0.5203125, 0.3625, 0.540625, 0.4609375, 0.5234375, 0.5265625, 0.584375, 0.509375, 0.5828125, 0.5578125, 0.3703125, 0.5828125, 0.553125, 0.2234375, 0.24375, 0.4890625, 0.2234375, 0.8453125, 0.553125, 0.58125, 0.584375, 0.5828125, 0.353125, 0.453125, 0.378125, 0.553125, 0.5015625, 0.6984375, 0.4875, 0.4984375, 0.459375, 0.3953125, 0.2921875, 0.3953125, 0.58125],
    avg: 0.5341940789473685
  },
  "sans-serif": {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.278125, 0.278125, 0.35625, 0.55625, 0.55625, 0.890625, 0.6671875, 0.1921875, 0.334375, 0.334375, 0.390625, 0.584375, 0.278125, 0.334375, 0.278125, 0.303125, 0.55625, 0.55625, 0.55625, 0.55625, 0.55625, 0.55625, 0.55625, 0.55625, 0.55625, 0.55625, 0.278125, 0.278125, 0.5859375, 0.584375, 0.5859375, 0.55625, 1.015625, 0.6671875, 0.6671875, 0.7234375, 0.7234375, 0.6671875, 0.6109375, 0.778125, 0.7234375, 0.278125, 0.5, 0.6671875, 0.55625, 0.834375, 0.7234375, 0.778125, 0.6671875, 0.778125, 0.7234375, 0.6671875, 0.6109375, 0.7234375, 0.6671875, 0.9453125, 0.6671875, 0.6671875, 0.6109375, 0.278125, 0.35625, 0.278125, 0.478125, 0.55625, 0.334375, 0.55625, 0.55625, 0.5, 0.55625, 0.55625, 0.278125, 0.55625, 0.55625, 0.2234375, 0.2421875, 0.5, 0.2234375, 0.834375, 0.55625, 0.55625, 0.55625, 0.55625, 0.334375, 0.5, 0.278125, 0.55625, 0.5, 0.7234375, 0.5, 0.5, 0.5, 0.35625, 0.2609375, 0.3546875, 0.590625],
    avg: 0.5293256578947368
  },
  Seravek: {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.215625, 0.296875, 0.4171875, 0.6734375, 0.4953125, 0.9125, 0.740625, 0.2421875, 0.3375, 0.3375, 0.409375, 0.60625, 0.2609375, 0.35625, 0.25625, 0.41875, 0.5921875, 0.3515625, 0.475, 0.4875, 0.5375, 0.509375, 0.5484375, 0.4546875, 0.5421875, 0.5484375, 0.25625, 0.2546875, 0.5875, 0.6171875, 0.5875, 0.4578125, 0.8140625, 0.6765625, 0.5703125, 0.6109375, 0.684375, 0.5109375, 0.4953125, 0.678125, 0.6859375, 0.2625, 0.2625, 0.5859375, 0.4734375, 0.846875, 0.709375, 0.740625, 0.509375, 0.740625, 0.584375, 0.5015625, 0.528125, 0.675, 0.5953125, 0.9453125, 0.596875, 0.540625, 0.540625, 0.359375, 0.4203125, 0.359375, 0.5109375, 0.421875, 0.4046875, 0.5015625, 0.5421875, 0.446875, 0.5453125, 0.484375, 0.38125, 0.5140625, 0.5546875, 0.240625, 0.2640625, 0.490625, 0.2765625, 0.8625, 0.5546875, 0.546875, 0.5453125, 0.5453125, 0.3625, 0.41875, 0.3890625, 0.5453125, 0.4703125, 0.7546875, 0.4921875, 0.4609375, 0.453125, 0.4015625, 0.2640625, 0.4015625, 0.58125],
    avg: 0.5044078947368421
  },
  serif: {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.2484375, 0.334375, 0.409375, 0.5, 0.5, 0.834375, 0.778125, 0.18125, 0.334375, 0.334375, 0.5, 0.5640625, 0.25, 0.334375, 0.25, 0.278125, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.278125, 0.278125, 0.5640625, 0.5640625, 0.5640625, 0.4453125, 0.921875, 0.7234375, 0.6671875, 0.6671875, 0.7234375, 0.6109375, 0.55625, 0.7234375, 0.7234375, 0.334375, 0.390625, 0.7234375, 0.6109375, 0.890625, 0.7234375, 0.7234375, 0.55625, 0.7234375, 0.6671875, 0.55625, 0.6109375, 0.7234375, 0.7234375, 0.9453125, 0.7234375, 0.7234375, 0.6109375, 0.334375, 0.340625, 0.334375, 0.4703125, 0.5, 0.3453125, 0.4453125, 0.5, 0.4453125, 0.5, 0.4453125, 0.3828125, 0.5, 0.5, 0.278125, 0.3359375, 0.5, 0.278125, 0.778125, 0.5, 0.5, 0.5, 0.5, 0.3375, 0.390625, 0.2796875, 0.5, 0.5, 0.7234375, 0.5, 0.5, 0.4453125, 0.48125, 0.2015625, 0.48125, 0.5421875],
    avg: 0.5126315789473684
  },
  Tahoma: {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.3109375, 0.3328125, 0.4015625, 0.728125, 0.546875, 0.9765625, 0.70625, 0.2109375, 0.3828125, 0.3828125, 0.546875, 0.728125, 0.303125, 0.3640625, 0.303125, 0.3953125, 0.546875, 0.546875, 0.546875, 0.546875, 0.546875, 0.546875, 0.546875, 0.546875, 0.546875, 0.546875, 0.3546875, 0.3546875, 0.728125, 0.728125, 0.728125, 0.475, 0.909375, 0.6109375, 0.590625, 0.6015625, 0.6796875, 0.5625, 0.521875, 0.66875, 0.6765625, 0.3734375, 0.4171875, 0.6046875, 0.4984375, 0.771875, 0.66875, 0.7078125, 0.5515625, 0.7078125, 0.6375, 0.5578125, 0.5875, 0.65625, 0.60625, 0.903125, 0.58125, 0.5890625, 0.559375, 0.3828125, 0.39375, 0.3828125, 0.728125, 0.5625, 0.546875, 0.525, 0.553125, 0.4625, 0.553125, 0.5265625, 0.3546875, 0.553125, 0.5578125, 0.2296875, 0.328125, 0.51875, 0.2296875, 0.840625, 0.5578125, 0.54375, 0.553125, 0.553125, 0.3609375, 0.446875, 0.3359375, 0.5578125, 0.4984375, 0.7421875, 0.4953125, 0.4984375, 0.4453125, 0.48125, 0.3828125, 0.48125, 0.728125],
    avg: 0.5384374999999998
  },
  "Times New Roman": {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.2484375, 0.334375, 0.409375, 0.5, 0.5, 0.834375, 0.778125, 0.18125, 0.334375, 0.334375, 0.5, 0.5640625, 0.25, 0.334375, 0.25, 0.28125, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.278125, 0.278125, 0.5640625, 0.5640625, 0.5640625, 0.4453125, 0.921875, 0.7234375, 0.6671875, 0.6671875, 0.7234375, 0.6109375, 0.55625, 0.7234375, 0.7234375, 0.334375, 0.390625, 0.73125, 0.6109375, 0.890625, 0.7375, 0.7234375, 0.55625, 0.7234375, 0.6765625, 0.55625, 0.6109375, 0.7234375, 0.7234375, 0.9453125, 0.7234375, 0.7234375, 0.6109375, 0.334375, 0.28125, 0.334375, 0.4703125, 0.51875, 0.334375, 0.4453125, 0.503125, 0.4453125, 0.503125, 0.4453125, 0.4359375, 0.5, 0.5, 0.278125, 0.35625, 0.50625, 0.278125, 0.778125, 0.5, 0.5, 0.5046875, 0.5, 0.340625, 0.390625, 0.2796875, 0.5, 0.5, 0.7234375, 0.5, 0.5, 0.4453125, 0.48125, 0.2015625, 0.48125, 0.5421875],
    avg: 0.5134375
  },
  "Trebuchet MS": {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.3015625, 0.3671875, 0.325, 0.53125, 0.525, 0.6015625, 0.70625, 0.1609375, 0.3671875, 0.3671875, 0.3671875, 0.525, 0.3671875, 0.3671875, 0.3671875, 0.525, 0.525, 0.525, 0.525, 0.525, 0.525, 0.525, 0.525, 0.525, 0.525, 0.525, 0.3671875, 0.3671875, 0.525, 0.525, 0.525, 0.3671875, 0.771875, 0.590625, 0.5671875, 0.5984375, 0.6140625, 0.5359375, 0.525, 0.6765625, 0.6546875, 0.2796875, 0.4765625, 0.5765625, 0.5078125, 0.7109375, 0.6390625, 0.675, 0.5578125, 0.7421875, 0.5828125, 0.48125, 0.58125, 0.6484375, 0.5875, 0.853125, 0.5578125, 0.5703125, 0.5515625, 0.3671875, 0.3578125, 0.3671875, 0.525, 0.53125, 0.525, 0.5265625, 0.5578125, 0.4953125, 0.5578125, 0.546875, 0.375, 0.503125, 0.546875, 0.2859375, 0.3671875, 0.5046875, 0.2953125, 0.83125, 0.546875, 0.5375, 0.5578125, 0.5578125, 0.3890625, 0.40625, 0.396875, 0.546875, 0.490625, 0.7453125, 0.5015625, 0.49375, 0.475, 0.3671875, 0.525, 0.3671875, 0.525],
    avg: 0.5085197368421052
  },
  Verdana: {
    widths: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.35, 0.39375, 0.459375, 0.81875, 0.6359375, 1.0765625, 0.759375, 0.26875, 0.4546875, 0.4546875, 0.6359375, 0.81875, 0.3640625, 0.4546875, 0.3640625, 0.4703125, 0.6359375, 0.6359375, 0.6359375, 0.6359375, 0.6359375, 0.6359375, 0.6359375, 0.6359375, 0.6359375, 0.6359375, 0.4546875, 0.4546875, 0.81875, 0.81875, 0.81875, 0.546875, 1, 0.684375, 0.6859375, 0.6984375, 0.771875, 0.6328125, 0.575, 0.7765625, 0.7515625, 0.421875, 0.4546875, 0.69375, 0.5578125, 0.84375, 0.7484375, 0.7875, 0.603125, 0.7875, 0.7, 0.684375, 0.6171875, 0.7328125, 0.684375, 0.9890625, 0.6859375, 0.615625, 0.6859375, 0.4546875, 0.46875, 0.4546875, 0.81875, 0.6421875, 0.6359375, 0.6015625, 0.6234375, 0.521875, 0.6234375, 0.596875, 0.384375, 0.6234375, 0.6328125, 0.275, 0.3765625, 0.5921875, 0.275, 0.9734375, 0.6328125, 0.6078125, 0.6234375, 0.6234375, 0.43125, 0.521875, 0.3953125, 0.6328125, 0.5921875, 0.81875, 0.5921875, 0.5921875, 0.5265625, 0.6359375, 0.4546875, 0.6359375, 0.81875],
    avg: 0.6171875000000003
  }
};
var absoluteMeasurementUnitsToPixels = {
  mm: 3.8,
  sm: 38,
  pt: 1.33,
  pc: 16,
  in: 96,
  px: 1
};
var relativeMeasurementUnitsCoef = {
  em: 1,
  ex: 0.5
};
var coefficients = {
  heightOverlapCoef: 1.05,
  // Coefficient for height value to prevent overlap.
  lineCapitalCoef: 1.15
  // Coefficient for height value. Reserve space for capital chars.
};
var defaultStyle = {
  lineHeight: 1,
  letterSpacing: "0px",
  fontSize: 0,
  angle: 0,
  fontFamily: ""
};
var _degreeToRadian = (angle) => angle * Math.PI / 180;
var _getFontData = (fontFamily) => {
  const possibleFonts = fontFamily.split(",").map((f) => f.replace(/'|"/g, ""));
  const fontMatch = possibleFonts.find((f) => fonts[f]) || "Helvetica";
  return fonts[fontMatch];
};
var _splitToLines = (text) => {
  return Array.isArray(text) ? text : text.toString().split(/\r\n|\r|\n/g);
};
var _getSizeWithRotate = (axisSize, dependentSize, angle) => {
  const angleInRadian = _degreeToRadian(angle);
  return Math.abs(Math.cos(angleInRadian) * axisSize) + Math.abs(Math.sin(angleInRadian) * dependentSize);
};
var convertLengthToPixels = (length, fontSize3) => {
  var _a;
  const attribute = (_a = length.match(/[a-zA-Z%]+/)) == null ? void 0 : _a[0];
  const value = Number(length.match(/[0-9.,]+/));
  let result;
  if (!attribute) {
    result = value || 0;
  } else if (absoluteMeasurementUnitsToPixels.hasOwnProperty(attribute)) {
    result = value * absoluteMeasurementUnitsToPixels[attribute];
  } else if (relativeMeasurementUnitsCoef.hasOwnProperty(attribute)) {
    result = (fontSize3 ? value * fontSize3 : value * defaultStyle.fontSize) * relativeMeasurementUnitsCoef[attribute];
  } else {
    result = value;
  }
  return result;
};
var _prepareParams = (inputStyle, index) => {
  const lineStyle = Array.isArray(inputStyle) ? inputStyle[index] : inputStyle;
  const style = (0, import_defaults8.default)({}, lineStyle, defaultStyle);
  return Object.assign({}, style, {
    fontFamily: style.fontFamily,
    letterSpacing: typeof style.letterSpacing === "number" ? style.letterSpacing : convertLengthToPixels(String(style.letterSpacing), style.fontSize),
    fontSize: typeof style.fontSize === "number" ? style.fontSize : convertLengthToPixels(String(style.fontSize))
  });
};
var _approximateTextWidthInternal = (text, style) => {
  if (text === void 0 || text === "" || text === null) {
    return 0;
  }
  const widths = _splitToLines(text).map((line, index) => {
    const len = line.toString().length;
    const {
      fontSize: fontSize3,
      letterSpacing: letterSpacing3,
      fontFamily
    } = _prepareParams(style, index);
    const fontData = _getFontData(fontFamily);
    const width = line.toString().split("").map((c) => {
      return c.charCodeAt(0) < fontData.widths.length ? fontData.widths[c.charCodeAt(0)] : fontData.avg;
    }).reduce((cur, acc) => acc + cur, 0) * fontSize3;
    return width + letterSpacing3 * Math.max(len - 1, 0);
  });
  return Math.max(...widths);
};
var _approximateTextHeightInternal = (text, style) => {
  if (text === void 0 || text === "" || text === null) {
    return 0;
  }
  return _splitToLines(text).reduce((total, line, index) => {
    const lineStyle = _prepareParams(style, index);
    const containsCaps = line.toString().match(/[(A-Z)(0-9)]/);
    const height = containsCaps ? lineStyle.fontSize * coefficients.lineCapitalCoef : lineStyle.fontSize;
    return total + lineStyle.lineHeight * height;
  }, 0);
};
var _approximateDimensionsInternal = (text, style) => {
  const angle = Array.isArray(style) ? style[0] && style[0].angle : style && style.angle;
  const height = _approximateTextHeightInternal(text, style);
  const width = _approximateTextWidthInternal(text, style);
  const widthWithRotate = angle ? _getSizeWithRotate(width, height, angle) : width;
  const heightWithRotate = angle ? _getSizeWithRotate(height, width, angle) : height;
  return {
    width: widthWithRotate,
    height: heightWithRotate * coefficients.heightOverlapCoef
  };
};
var _getMeasurementContainer = (0, import_memoize.default)(() => {
  const element = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  element.setAttribute("xlink", "http://www.w3.org/1999/xlink");
  element.setAttribute("width", "300");
  element.setAttribute("height", "300");
  element.setAttribute("viewBox", "0 0 300 300");
  element.setAttribute("aria-hidden", "true");
  const containerElement = document.createElementNS("http://www.w3.org/2000/svg", "text");
  element.appendChild(containerElement);
  element.style.position = "fixed";
  element.style.top = "-9999px";
  element.style.left = "-9999px";
  document.body.appendChild(element);
  return containerElement;
});
var styleToKeyComponent = (style) => {
  if (!style) {
    return "null";
  }
  return `${style.angle}:${style.fontFamily}:${style.fontSize}:${style.letterSpacing}:${style.lineHeight}`;
};
var _measureDimensionsInternal = (0, import_memoize.default)((text, style) => {
  var _a, _b;
  let containerElement = _getMeasurementContainer();
  if (!containerElement.isConnected) {
    (_b = (_a = _getMeasurementContainer.cache).clear) == null ? void 0 : _b.call(_a);
    containerElement = _getMeasurementContainer();
  }
  const lines = _splitToLines(text);
  let heightAcc = 0;
  for (const [i, line] of lines.entries()) {
    const textElement = document.createElementNS("http://www.w3.org/2000/svg", "tspan");
    const params = _prepareParams(style, i);
    textElement.style.fontFamily = params.fontFamily;
    textElement.style.fontSize = `${params.fontSize}px`;
    textElement.style.lineHeight = params.lineHeight;
    textElement.style.fontFamily = params.fontFamily;
    textElement.style.letterSpacing = params.letterSpacing;
    textElement.textContent = line;
    textElement.setAttribute("x", "0");
    textElement.setAttribute("y", `${heightAcc}`);
    containerElement.appendChild(textElement);
    heightAcc += params.lineHeight * textElement.getBoundingClientRect().height;
  }
  const {
    width
  } = containerElement.getBoundingClientRect();
  containerElement.innerHTML = "";
  return {
    width: (style == null ? void 0 : style.angle) ? _getSizeWithRotate(width, heightAcc, style == null ? void 0 : style.angle) : width,
    height: (style == null ? void 0 : style.angle) ? _getSizeWithRotate(heightAcc, width, style == null ? void 0 : style.angle) : heightAcc
  };
}, (text, style) => {
  const totalText = Array.isArray(text) ? text.join() : text;
  const totalStyle = Array.isArray(style) ? style.map(styleToKeyComponent).join() : styleToKeyComponent(style);
  return `${totalText}::${totalStyle}`;
});
var _approximateTextSizeInternal = {
  impl: function(text, style, __debugForceApproximate) {
    if (__debugForceApproximate === void 0) {
      __debugForceApproximate = false;
    }
    const isClient = typeof window !== "undefined" && typeof window.document !== "undefined" && typeof window.document.createElement !== "undefined";
    if (!isClient || __debugForceApproximate) {
      return _approximateDimensionsInternal(text, style);
    }
    return _measureDimensionsInternal(text, style);
  }
};
var approximateTextSize = (text, style) => _approximateTextSizeInternal.impl(text, style);

// node_modules/victory-core/es/victory-util/wrapper.js
var wrapper_exports = {};
__export(wrapper_exports, {
  addBinsToParentPropsIfHistogram: () => addBinsToParentPropsIfHistogram,
  getAllEvents: () => getAllEvents,
  getCategories: () => getCategories2,
  getCategoryAndAxisStringsFromChildren: () => getCategoryAndAxisStringsFromChildren,
  getChildStyle: () => getChildStyle,
  getColor: () => getColor,
  getData: () => getData2,
  getDataFromChildren: () => getDataFromChildren,
  getDefaultDomainPadding: () => getDefaultDomainPadding,
  getDomain: () => getDomain3,
  getDomainFromChildren: () => getDomainFromChildren,
  getScale: () => getScale,
  getStringsFromCategories: () => getStringsFromCategories2,
  getStringsFromChildren: () => getStringsFromChildren,
  getStringsFromData: () => getStringsFromData2,
  getStyle: () => getStyle,
  getWidth: () => getWidth
});
var import_isPlainObject5 = __toESM(require_isPlainObject());
var import_uniqBy = __toESM(require_uniqBy());
var import_groupBy = __toESM(require_groupBy());
var import_uniq4 = __toESM(require_uniq());
var import_defaults9 = __toESM(require_defaults());
var import_react14 = __toESM(require_react());
function addBinsToParentPropsIfHistogram(_ref) {
  let {
    children,
    props,
    childComponents,
    parentProps
  } = _ref;
  const someChildrenAreHistograms = children.some((child) => {
    return child.type && child.type.role === "histogram";
  });
  const allChildrenAreHistograms = someChildrenAreHistograms && children.length && children.every((child) => {
    return child.type && child.type.role === "histogram";
  });
  if (someChildrenAreHistograms && !allChildrenAreHistograms) {
    warn("VictoryHistogram only supports being stacked with other VictoryHistogram components. Check to make sure that you are only passing VictoryHistogram components to VictoryStack");
  }
  if (!allChildrenAreHistograms) {
    return parentProps;
  }
  let childBins = props.bins || childComponents[0].props.bins;
  if (!Array.isArray(childBins)) {
    const combinedData = children.reduce((memo, child) => {
      const xAccessor = createAccessor(child.props.x || "x");
      return memo.concat(child.props.data.map((datum) => ({
        x: xAccessor(datum)
      })));
    }, []);
    const getFormattedHistogramData = children[0].type.getFormattedData;
    childBins = getFormattedHistogramData({
      data: combinedData,
      bins: childBins
    }).reduce((memo, _ref2, index) => {
      let {
        x0,
        x1
      } = _ref2;
      return index === 0 ? memo.concat([x0, x1]) : memo.concat(x1);
    }, []);
  }
  return {
    ...parentProps,
    bins: childBins
  };
}
function getDataFromChildren(props, childComponents) {
  const {
    polar,
    startAngle,
    endAngle,
    categories,
    minDomain,
    maxDomain
  } = props;
  let parentProps = {
    polar,
    startAngle,
    endAngle,
    categories,
    minDomain,
    maxDomain
  };
  let stack = 0;
  const children = childComponents ? childComponents.slice(0) : import_react14.default.Children.toArray(props.children);
  parentProps = addBinsToParentPropsIfHistogram({
    children,
    props,
    childComponents,
    parentProps
  });
  const iteratee = (child, childName, parent) => {
    const childProps = Object.assign({}, child.props, parentProps);
    let childData;
    let childElement = child;
    if (!isDataComponent(child)) {
      return null;
    } else if (child.type && isFunction(child.type.getData)) {
      childElement = parent ? import_react14.default.cloneElement(child, parent.props) : child;
      childData = childElement.type.getData(childProps);
    } else {
      childData = getData(childProps);
    }
    stack += 1;
    return childData.map((datum, index) => Object.assign({
      _stack: stack,
      _group: index
    }, datum));
  };
  const stacked = children.filter((c) => c.type && c.type.role === "stack").length;
  const combine = (memo, val) => memo.concat((0, import_uniqBy.default)(val, "_group"));
  const datasets = reduceChildren(children, iteratee, props, [], combine);
  const group = stacked ? "_group" : "_stack";
  return Object.values((0, import_groupBy.default)(datasets, group));
}
function getData2(props, childComponents) {
  if (props.data) {
    return getData(props);
  }
  return getDataFromChildren(props, childComponents || import_react14.default.Children.toArray(props.children));
}
function getWidth(props, groupLength, seriesLength) {
  const {
    datasets,
    horizontal
  } = props;
  const range3 = horizontal ? getRange(props, "y") : getRange(props, "x");
  const extent2 = Math.abs(range3[1] - range3[0]);
  const seriesLengthValue = seriesLength !== void 0 ? seriesLength : Array.isArray(datasets[0]) && datasets[0].length || 1;
  const groupLengthValue = groupLength || datasets.length;
  const bars = groupLengthValue * seriesLengthValue;
  const barRatio = 0.5;
  return Math.round(barRatio * extent2 / bars);
}
function getDefaultDomainPadding(props, axis, childComponents) {
  if (props.polar || axis !== "x") {
    return void 0;
  }
  const groupComponent = childComponents.filter((child) => {
    return child.type && child.type.role && child.type.role === "group";
  });
  if (groupComponent.length < 1) {
    return void 0;
  }
  const {
    offset,
    children
  } = groupComponent[0].props;
  if (!offset) {
    return void 0;
  }
  const firstChild = Array.isArray(children) && children[0];
  if (!firstChild) {
    return void 0;
  }
  let barWidth = firstChild.props.barWidth;
  let dataLength = firstChild.props.data && firstChild.props.data.length || 1;
  if (firstChild && firstChild.type.role === "stack") {
    const nestedChild = firstChild.props.children && firstChild.props.children[0];
    if (!nestedChild) {
      return void 0;
    }
    barWidth = nestedChild.props.barWidth;
    dataLength = firstChild.props.children.length;
  }
  const width = barWidth || getWidth(props, children.length, dataLength);
  return {
    x: width * children.length / 2 + (offset - width * ((children.length - 1) / 2))
  };
}
function getDomainFromChildren(props, axis, childComponents) {
  const children = childComponents ? childComponents.slice(0) : import_react14.default.Children.toArray(props.children);
  const parentData = props.data ? getData(props) : void 0;
  const {
    polar,
    startAngle,
    endAngle,
    categories,
    minDomain,
    maxDomain,
    horizontal
  } = props;
  const baseParentProps = {
    horizontal,
    polar,
    startAngle,
    endAngle,
    minDomain,
    maxDomain,
    categories
  };
  const parentProps = parentData ? Object.assign(baseParentProps, {
    data: parentData
  }) : baseParentProps;
  const iteratee = (child) => {
    const sharedProps = Object.assign({}, child.props, parentProps);
    if (!isDomainComponent(child)) {
      return null;
    } else if (child.type && isFunction(child.type.getDomain)) {
      return child.props && child.type.getDomain(sharedProps, axis);
    }
    return getDomain(sharedProps, axis);
  };
  const childDomains = reduceChildren(children, iteratee, props);
  const min2 = childDomains.length === 0 ? 0 : getMinValue(childDomains);
  const max2 = childDomains.length === 0 ? 1 : getMaxValue(childDomains);
  return [min2, max2];
}
function getDomain3(props, axis, childComponents) {
  const children = childComponents || import_react14.default.Children.toArray(props.children);
  const propsDomain = getDomainFromProps(props, axis);
  const domainPadding = getDefaultDomainPadding(props, axis, children);
  let domain;
  if (propsDomain) {
    domain = propsDomain;
  } else {
    const minDomain = getMinFromProps(props, axis);
    const maxDomain = getMaxFromProps(props, axis);
    const dataset = (props.data || props.y) && getData(props);
    const dataDomain = dataset ? getDomainFromData(props, axis, dataset) : [];
    const childDomain = getDomainFromChildren(props, axis, children);
    const min2 = minDomain || getMinValue([...dataDomain, ...childDomain]);
    const max2 = maxDomain || getMaxValue([...dataDomain, ...childDomain]);
    domain = getDomainFromMinMax(min2, max2);
  }
  return formatDomain(domain, Object.assign({
    domainPadding
  }, props), axis);
}
function getScale(props, axis, childComponents) {
  if (props.data) {
    return getBaseScale(props, axis);
  }
  const children = childComponents ? childComponents.slice(0) : import_react14.default.Children.toArray(props.children);
  const iteratee = (child) => {
    const sharedProps = Object.assign({}, child.props, {
      horizontal: props.horizontal
    });
    return getScaleType(sharedProps, axis);
  };
  const childScale = (0, import_uniq4.default)(reduceChildren(children, iteratee, props));
  return childScale.length > 1 ? getScaleFromName("linear") : getScaleFromName(childScale[0]);
}
function getAllEvents(props) {
  const components = ["groupComponent", "containerComponent", "labelComponent"];
  const componentEvents = getComponentEvents(props, components);
  let events = props.events;
  if (Array.isArray(componentEvents)) {
    events = Array.isArray(props.events) ? componentEvents.concat(...props.events) : componentEvents;
  }
  return events || [];
}
function getColor(calculatedProps, child, index) {
  const {
    style
  } = calculatedProps;
  let {
    colorScale,
    color
  } = calculatedProps;
  if (style && style.data && style.data.fill) {
    return style.data.fill;
  }
  colorScale = child.props && child.props.colorScale ? child.props.colorScale : colorScale;
  color = child.props && child.props.color ? child.props.color : color;
  if (!colorScale && !color) {
    return void 0;
  }
  const colors3 = Array.isArray(colorScale) ? colorScale : getColorScale(colorScale);
  return color || colors3[index % colors3.length];
}
function getStyle(theme, style, role) {
  const defaultStyle2 = theme && theme[role] && theme[role].style ? theme[role].style : {};
  return getStyles(style, defaultStyle2);
}
function getChildStyle(child, index, calculatedProps) {
  const {
    style,
    role
  } = calculatedProps;
  const childStyle = child.props.style || {};
  if (Array.isArray(childStyle)) {
    return childStyle;
  }
  const childRole = child.type && child.type.role;
  const defaultFill = childRole === "stack" ? void 0 : getColor(calculatedProps, child, index);
  const defaultColor = childRole === "line" ? {
    fill: "none",
    stroke: defaultFill
  } : {
    fill: defaultFill
  };
  const dataWidth = role === "stack" ? {} : {
    width: getWidth(calculatedProps)
  };
  const dataStyle = (0, import_defaults9.default)({}, childStyle.data, Object.assign({}, dataWidth, style.data, defaultColor));
  const labelsStyle = (0, import_defaults9.default)({}, childStyle.labels, style.labels);
  return {
    ...childStyle,
    parent: style.parent,
    data: dataStyle,
    labels: labelsStyle
  };
}
function getStringsFromCategories2(childComponents, axis) {
  const iteratee = (child) => {
    const childProps = child.props || {};
    if (!isDomainComponent(child) || !childProps.categories) {
      return null;
    }
    const categories = childProps.categories && !Array.isArray(childProps.categories) ? childProps.categories[axis] : childProps.props.categories;
    const categoryStrings = categories && categories.filter((val) => typeof val === "string");
    return categoryStrings ? removeUndefined(categoryStrings) : [];
  };
  return reduceChildren(childComponents.slice(0), iteratee);
}
function getStringsFromData2(childComponents) {
  const iteratee = (child) => {
    const childProps = child.props || {};
    let data;
    if (!isDataComponent(child)) {
      return null;
    } else if (child.type && isFunction(child.type.getData)) {
      data = child.type.getData(childProps);
    } else {
      data = getData(childProps);
    }
    return data.map((d) => ({
      x: d.xName,
      y: d.yName
    }));
  };
  const initialMemo = {
    x: [],
    y: []
  };
  const combine = (memo, datum) => {
    const x2 = Array.isArray(datum) ? datum.map((d) => d.x).filter(Boolean) : datum.x;
    const y2 = Array.isArray(datum) ? datum.map((d) => d.y).filter(Boolean) : datum.y;
    return {
      x: x2 !== void 0 ? memo.x.concat(x2) : memo.x,
      y: y2 !== void 0 ? memo.y.concat(y2) : memo.y
    };
  };
  return reduceChildren(childComponents.slice(0), iteratee, {}, initialMemo, combine);
}
function getCategoryAndAxisStringsFromChildren(props, axis, childComponents) {
  const categories = (0, import_isPlainObject5.default)(props.categories) ? props.categories[axis] : props.categories;
  const axisComponent = getAxisComponent(childComponents, axis);
  const axisStrings = axisComponent ? getStringsFromAxes(axisComponent.props, axis) : [];
  const categoryStrings = categories || getStringsFromCategories2(childComponents, axis);
  return (0, import_uniq4.default)([...categoryStrings, ...axisStrings].flat());
}
function getStringsFromChildren(props, childComponents) {
  const children = childComponents || import_react14.default.Children.toArray(props.children);
  const xStrings = getCategoryAndAxisStringsFromChildren(props, "x", children);
  const yStrings = getCategoryAndAxisStringsFromChildren(props, "y", children);
  const dataStrings = getStringsFromData2(children);
  return {
    x: (0, import_uniq4.default)([...xStrings, ...dataStrings.x].flat()),
    y: (0, import_uniq4.default)([...yStrings, ...dataStrings.y].flat())
  };
}
function getCategories2(props, childComponents, allStrings) {
  const xPropCategories = props.categories && !Array.isArray(props.categories) ? props.categories.x : props.categories;
  const yPropCategories = props.categories && !Array.isArray(props.categories) ? props.categories.y : props.categories;
  const fallbackRequired = !xPropCategories || !yPropCategories;
  const fallbackProps22 = fallbackRequired ? allStrings || getStringsFromChildren(props, childComponents) : {};
  const xCategories = xPropCategories || fallbackProps22.x;
  const yCategories = yPropCategories || fallbackProps22.y;
  return {
    x: xCategories.length > 0 ? xCategories : void 0,
    y: yCategories.length > 0 ? yCategories : void 0
  };
}

// node_modules/victory-core/es/victory-portal/portal-outlet.js
var import_react16 = __toESM(require_react());

// node_modules/victory-core/es/victory-portal/portal-context.js
var import_react15 = __toESM(require_react());
var PortalContext = import_react15.default.createContext(void 0);
PortalContext.displayName = "PortalContext";
var usePortalContext = () => {
  const context = import_react15.default.useContext(PortalContext);
  return context;
};
var PortalProvider = (_ref) => {
  let {
    children
  } = _ref;
  const [portalChildren, setPortalChildren] = import_react15.default.useState(/* @__PURE__ */ new Map());
  const addChild = import_react15.default.useCallback((id, element) => {
    setPortalChildren((prevChildren) => {
      const nextChildren = new Map(prevChildren);
      nextChildren.set(id, element);
      return nextChildren;
    });
  }, [setPortalChildren]);
  const removeChild = import_react15.default.useCallback((id) => {
    setPortalChildren((prevChildren) => {
      const nextChildren = new Map(prevChildren);
      nextChildren.delete(id);
      return nextChildren;
    });
  }, [setPortalChildren]);
  const contextValue = import_react15.default.useMemo(() => ({
    addChild,
    removeChild,
    children: portalChildren
  }), [addChild, removeChild, portalChildren]);
  return import_react15.default.createElement(PortalContext.Provider, {
    value: contextValue
  }, children);
};

// node_modules/victory-core/es/victory-portal/portal-outlet.js
var PortalOutlet = (_ref) => {
  let {
    as: portalComponent,
    ...props
  } = _ref;
  const portalContext = usePortalContext();
  if (!portalContext) {
    return null;
  }
  const children = Array.from(portalContext.children.values());
  return import_react16.default.cloneElement(portalComponent, props, children);
};

// node_modules/victory-core/es/victory-container/victory-container.js
function _extends3() {
  _extends3 = Object.assign ? Object.assign.bind() : function(target) {
    for (var i = 1; i < arguments.length; i++) {
      var source = arguments[i];
      for (var key in source) {
        if (Object.prototype.hasOwnProperty.call(source, key)) {
          target[key] = source[key];
        }
      }
    }
    return target;
  };
  return _extends3.apply(this, arguments);
}
var defaultProps = {
  className: "VictoryContainer",
  portalComponent: import_react17.default.createElement(Portal, null),
  portalZIndex: 99,
  responsive: true,
  role: "img"
};
function useVictoryContainer(initialProps) {
  const props = {
    ...defaultProps,
    ...initialProps
  };
  const {
    title,
    desc,
    width,
    height,
    responsive
  } = props;
  const localContainerRef = (0, import_react17.useRef)(null);
  const generatedId = (0, import_react17.useRef)((0, import_uniqueId.default)("victory-container-"));
  const containerId = props.containerId ?? generatedId.current;
  const getIdForElement = (elName) => `${containerId}-${elName}`;
  const userProps = getSafeUserProps(props);
  const dimensions = responsive ? {
    width: "100%",
    height: "100%"
  } : {
    width,
    height
  };
  const viewBox = responsive ? `0 0 ${width} ${height}` : void 0;
  const preserveAspectRatio = responsive ? props.preserveAspectRatio : void 0;
  const ariaLabelledBy = [title && getIdForElement("title"), props["aria-labelledby"]].filter(Boolean).join(" ") || void 0;
  const ariaDescribedBy = [desc && getIdForElement("desc"), props["aria-describedby"]].filter(Boolean).join(" ") || void 0;
  const titleId = getIdForElement("title");
  const descId = getIdForElement("desc");
  return {
    ...props,
    titleId,
    descId,
    dimensions,
    viewBox,
    preserveAspectRatio,
    ariaLabelledBy,
    ariaDescribedBy,
    userProps,
    localContainerRef
  };
}
var VictoryContainer = (initialProps) => {
  const {
    role,
    title,
    desc,
    children,
    className,
    portalZIndex,
    portalComponent,
    width,
    height,
    style,
    tabIndex,
    responsive,
    events,
    ouiaId,
    ouiaSafe,
    ouiaType,
    dimensions,
    ariaDescribedBy,
    ariaLabelledBy,
    viewBox,
    preserveAspectRatio,
    userProps,
    titleId,
    descId,
    containerRef,
    localContainerRef
  } = useVictoryContainer(initialProps);
  import_react17.default.useEffect(() => {
    if (!(events == null ? void 0 : events.onWheel)) return;
    const handleWheel = (e) => e.preventDefault();
    const container = localContainerRef == null ? void 0 : localContainerRef.current;
    container == null ? void 0 : container.addEventListener("wheel", handleWheel);
    return () => {
      container == null ? void 0 : container.removeEventListener("wheel", handleWheel);
    };
  }, []);
  return import_react17.default.createElement("div", {
    className,
    style: {
      ...style,
      width: responsive ? style == null ? void 0 : style.width : dimensions.width,
      height: responsive ? style == null ? void 0 : style.height : dimensions.height,
      pointerEvents: "none",
      touchAction: "none",
      position: "relative"
    },
    "data-ouia-component-id": ouiaId,
    "data-ouia-component-type": ouiaType,
    "data-ouia-safe": ouiaSafe,
    ref: mergeRefs([localContainerRef, containerRef])
  }, import_react17.default.createElement(PortalProvider, null, import_react17.default.createElement("svg", _extends3({
    width,
    height,
    tabIndex,
    role,
    "aria-labelledby": ariaLabelledBy,
    "aria-describedby": ariaDescribedBy,
    viewBox,
    preserveAspectRatio,
    style: {
      ...dimensions,
      pointerEvents: "all"
    }
  }, userProps, events), title ? import_react17.default.createElement("title", {
    id: titleId
  }, title) : null, desc ? import_react17.default.createElement("desc", {
    id: descId
  }, desc) : null, children), import_react17.default.createElement("div", {
    style: {
      ...dimensions,
      zIndex: portalZIndex,
      position: "absolute",
      top: 0,
      left: 0
    }
  }, import_react17.default.createElement(PortalOutlet, {
    as: portalComponent,
    width,
    height,
    viewBox,
    preserveAspectRatio,
    style: {
      ...dimensions,
      overflow: "visible"
    }
  }))));
};
VictoryContainer.role = "container";

// node_modules/victory-core/es/victory-label/victory-label.js
var import_isEmpty4 = __toESM(require_isEmpty());
var import_defaults11 = __toESM(require_defaults());
var import_react22 = __toESM(require_react());

// node_modules/victory-core/es/victory-portal/victory-portal.js
var import_defaults10 = __toESM(require_defaults());
var import_react18 = __toESM(require_react());
var defaultProps2 = {
  groupComponent: import_react18.default.createElement("g", null)
};
var VictoryPortal = (initialProps) => {
  const props = {
    ...defaultProps2,
    ...initialProps
  };
  const id = import_react18.default.useId();
  const portalContext = usePortalContext();
  if (!portalContext) {
    const msg = "`renderInPortal` is not supported outside of `VictoryContainer`. Component will be rendered in place";
    warn(msg);
  }
  const children = Array.isArray(props.children) ? props.children[0] : props.children;
  const {
    groupComponent
  } = props;
  const childProps = children && children.props || {};
  const standardProps = childProps.groupComponent ? {
    groupComponent,
    standalone: false
  } : {};
  const newProps = (0, import_defaults10.default)(standardProps, childProps, omit(props, ["children", "groupComponent"]), {
    key: childProps.key ?? id
  });
  const child = children && import_react18.default.cloneElement(children, newProps);
  import_react18.default.useEffect(() => {
    portalContext == null ? void 0 : portalContext.addChild(id, child);
  }, [props.children]);
  import_react18.default.useEffect(() => {
    return () => portalContext == null ? void 0 : portalContext.removeChild(id);
  }, []);
  return portalContext ? null : child;
};
VictoryPortal.role = "portal";

// node_modules/victory-core/es/victory-primitives/rect.js
var import_react19 = __toESM(require_react());
function _extends4() {
  _extends4 = Object.assign ? Object.assign.bind() : function(target) {
    for (var i = 1; i < arguments.length; i++) {
      var source = arguments[i];
      for (var key in source) {
        if (Object.prototype.hasOwnProperty.call(source, key)) {
          target[key] = source[key];
        }
      }
    }
    return target;
  };
  return _extends4.apply(this, arguments);
}
var Rect = (0, import_react19.forwardRef)((props, ref) => {
  var _a;
  const {
    desc,
    id,
    tabIndex,
    origin,
    ...rest
  } = props;
  const svgProps = {
    vectorEffect: "non-scaling-stroke",
    id: (_a = evaluateProp(id, props)) == null ? void 0 : _a.toString(),
    tabIndex: evaluateProp(tabIndex, props),
    ...rest
  };
  return desc ? import_react19.default.createElement("rect", _extends4({}, svgProps, {
    ref
  }), import_react19.default.createElement("desc", null, desc)) : import_react19.default.createElement("rect", _extends4({}, svgProps, {
    ref
  }));
});

// node_modules/victory-core/es/victory-primitives/text.js
var import_react20 = __toESM(require_react());
var Text = (props) => {
  var _a;
  const {
    children,
    desc,
    id,
    origin,
    tabIndex,
    title,
    ...rest
  } = props;
  const svgProps = {
    id: (_a = evaluateProp(id, props)) == null ? void 0 : _a.toString(),
    tabIndex: evaluateProp(tabIndex, props),
    ...rest
  };
  return import_react20.default.createElement("text", svgProps, title && import_react20.default.createElement("title", null, title), desc && import_react20.default.createElement("desc", null, desc), children);
};

// node_modules/victory-core/es/victory-primitives/tspan.js
var import_react21 = __toESM(require_react());
var TSpan = (props) => {
  var _a;
  const {
    desc,
    id,
    tabIndex,
    origin,
    ...rest
  } = props;
  const svgProps = {
    id: (_a = evaluateProp(id, props)) == null ? void 0 : _a.toString(),
    tabIndex: evaluateProp(tabIndex, props),
    ...rest
  };
  return import_react21.default.createElement("tspan", svgProps);
};

// node_modules/victory-core/es/victory-label/victory-label.js
var defaultStyles = {
  fill: "#252525",
  fontSize: 14,
  fontFamily: "'Gill Sans', 'Gill Sans MT', 'Ser­avek', 'Trebuchet MS', sans-serif",
  stroke: "transparent"
};
var getPosition2 = (props, dimension) => {
  if (!props.datum) {
    return 0;
  }
  const scaledPoint = scalePoint(props, props.datum);
  return scaledPoint[dimension];
};
var getFontSize = (style) => {
  const baseSize = style && style.fontSize;
  if (typeof baseSize === "number") {
    return baseSize;
  } else if (baseSize === void 0 || baseSize === null) {
    return defaultStyles.fontSize;
  } else if (typeof baseSize === "string") {
    const fontSize3 = Number(baseSize.replace("px", ""));
    if (!isNaN(fontSize3)) {
      return fontSize3;
    }
    warn("fontSize should be expressed as a number of pixels");
    return defaultStyles.fontSize;
  }
  return defaultStyles.fontSize;
};
var getSingleValue = function(prop, index) {
  if (index === void 0) {
    index = 0;
  }
  return Array.isArray(prop) ? prop[index] || prop[0] : prop;
};
var shouldUseMultilineBackgrounds = (props) => {
  const {
    backgroundStyle,
    backgroundPadding
  } = props;
  return Array.isArray(backgroundStyle) && !(0, import_isEmpty4.default)(backgroundStyle) || Array.isArray(backgroundPadding) && !(0, import_isEmpty4.default)(backgroundPadding);
};
var getStyles2 = (style, props) => {
  if (props.disableInlineStyles) {
    const baseStyles = evaluateStyle(style, props);
    return {
      // Font size is necessary to calculate the y position of the label
      fontSize: getFontSize(baseStyles)
    };
  }
  const getSingleStyle = (s) => {
    const baseStyles = evaluateStyle(s ? (0, import_defaults11.default)({}, s, defaultStyles) : defaultStyles, props);
    return Object.assign({}, baseStyles, {
      fontSize: getFontSize(baseStyles)
    });
  };
  return Array.isArray(style) && !(0, import_isEmpty4.default)(style) ? style.map((s) => getSingleStyle(s)) : getSingleStyle(style);
};
var getBackgroundStyles = (style, props) => {
  if (!style) {
    return void 0;
  }
  return Array.isArray(style) && !(0, import_isEmpty4.default)(style) ? style.map((s) => evaluateStyle(s, props)) : evaluateStyle(style, props);
};
var getBackgroundPadding = (props) => {
  if (props.backgroundPadding && Array.isArray(props.backgroundPadding)) {
    return props.backgroundPadding.map((backgroundPadding) => {
      const padding3 = evaluateProp(backgroundPadding, props);
      return getPadding({
        padding: padding3
      });
    });
  }
  const padding2 = evaluateProp(props.backgroundPadding, props);
  return getPadding({
    padding: padding2
  });
};
var getLineHeight = (props) => {
  const lineHeight = evaluateProp(props.lineHeight, props);
  if (Array.isArray(lineHeight)) {
    return (0, import_isEmpty4.default)(lineHeight) ? [1] : lineHeight;
  }
  return lineHeight;
};
var getContent = (text, props) => {
  if (text === void 0 || text === null) {
    return void 0;
  }
  if (Array.isArray(text)) {
    return text.map((line) => evaluateProp(line, props));
  }
  const child = evaluateProp(text, props);
  if (child === void 0 || child === null) {
    return void 0;
  }
  return Array.isArray(child) ? child : `${child}`.split("\n");
};
var getDy = (props, verticalAnchor, lineHeight) => {
  const dy = props.dy ? evaluateProp(props.dy, props) : 0;
  const length = props.inline ? 1 : props.text.length;
  const capHeight = evaluateProp(props.capHeight, props);
  const anchor = verticalAnchor ? evaluateProp(verticalAnchor, props) : "middle";
  const fontSizes = [...Array(length).keys()].map((i) => getSingleValue(props.style, i).fontSize);
  const lineHeights = [...Array(length).keys()].map((i) => getSingleValue(lineHeight, i));
  if (anchor === "start") {
    return dy + (capHeight / 2 + lineHeights[0] / 2) * fontSizes[0];
  } else if (props.inline) {
    return anchor === "end" ? dy + (capHeight / 2 - lineHeights[0] / 2) * fontSizes[0] : dy + capHeight / 2 * fontSizes[0];
  } else if (length === 1) {
    return anchor === "end" ? dy + (capHeight / 2 + (0.5 - length) * lineHeights[0]) * fontSizes[0] : dy + (capHeight / 2 + (0.5 - length / 2) * lineHeights[0]) * fontSizes[0];
  }
  const allHeights = [...Array(length).keys()].reduce((memo, i) => {
    return memo + (capHeight / 2 + (0.5 - length) * lineHeights[i]) * fontSizes[i] / length;
  }, 0);
  return anchor === "end" ? dy + allHeights : dy + allHeights / 2 + capHeight / 2 * lineHeights[length - 1] * fontSizes[length - 1];
};
var getTransform = (props, x2, y2) => {
  const {
    polar
  } = props;
  const style = getSingleValue(props.style);
  const defaultAngle = polar ? getPolarAngle(props) : 0;
  const baseAngle = style.angle === void 0 ? evaluateProp(props.angle, props) : style.angle;
  const angle = baseAngle === void 0 ? defaultAngle : baseAngle;
  const transform = props.transform || style.transform;
  const transformPart = transform && evaluateProp(transform, props);
  const rotatePart = angle && {
    rotate: [angle, x2, y2]
  };
  return transformPart || angle ? toTransformString(transformPart, rotatePart) : void 0;
};
var getXCoordinate = (calculatedProps, labelSizeWidth) => {
  const {
    direction,
    textAnchor,
    x: x2,
    dx
  } = calculatedProps;
  if (direction === "rtl") {
    return x2 - labelSizeWidth;
  }
  switch (textAnchor) {
    case "middle":
      return Math.round(x2 - labelSizeWidth / 2);
    case "end":
      return Math.round(x2 - labelSizeWidth);
    default:
      return x2 + (dx || 0);
  }
};
var getYCoordinate = (calculatedProps, textHeight) => {
  const {
    verticalAnchor,
    y: y2,
    originalDy = 0
  } = calculatedProps;
  const offset = y2 + originalDy;
  switch (verticalAnchor) {
    case "start":
      return Math.floor(offset);
    case "end":
      return Math.ceil(offset - textHeight);
    default:
      return Math.floor(offset - textHeight / 2);
  }
};
var getFullBackground = (calculatedProps, tspanValues) => {
  const {
    dx = 0,
    transform,
    backgroundComponent,
    backgroundStyle,
    inline,
    backgroundPadding,
    capHeight
  } = calculatedProps;
  const textSizes = tspanValues.map((tspan) => {
    return tspan.textSize;
  });
  const height = inline ? Math.max(...textSizes.map((size) => size.height)) : textSizes.reduce((memo, size, i) => {
    const capHeightAdjustment = i ? 0 : capHeight / 2;
    return memo + size.height * (tspanValues[i].lineHeight - capHeightAdjustment);
  }, 0);
  const width = inline ? textSizes.reduce((memo, size, index) => {
    const offset = index ? dx : 0;
    return memo + size.width + offset;
  }, 0) : Math.max(...textSizes.map((size) => size.width));
  const xCoordinate = getXCoordinate(calculatedProps, width);
  const yCoordinate = getYCoordinate(calculatedProps, height);
  const backgroundProps = {
    key: "background",
    height: height + backgroundPadding.top + backgroundPadding.bottom,
    style: backgroundStyle,
    transform,
    width: width + backgroundPadding.left + backgroundPadding.right,
    x: inline ? xCoordinate - backgroundPadding.left : xCoordinate + dx - backgroundPadding.left,
    y: yCoordinate
  };
  return import_react22.default.cloneElement(backgroundComponent, (0, import_defaults11.default)({}, backgroundComponent.props, backgroundProps));
};
var getInlineXOffset = (calculatedProps, textElements, index) => {
  const {
    textAnchor
  } = calculatedProps;
  const widths = textElements.map((t) => t.widthWithPadding);
  const totalWidth = widths.reduce((memo, width) => memo + width, 0);
  const centerOffset = -totalWidth / 2;
  switch (textAnchor) {
    case "start":
      return widths.reduce((memo, width, i) => i < index ? memo + width : memo, 0);
    case "end":
      return widths.reduce((memo, width, i) => i > index ? memo - width : memo, 0);
    default:
      return widths.reduce((memo, width, i) => {
        const offsetWidth = i < index ? width : 0;
        return i === index ? memo + width / 2 : memo + offsetWidth;
      }, centerOffset);
  }
};
var getChildBackgrounds = (calculatedProps, tspanValues) => {
  const {
    dy,
    dx,
    transform,
    backgroundStyle,
    backgroundPadding,
    backgroundComponent,
    inline,
    y: y2
  } = calculatedProps;
  const textElements = tspanValues.map((current, i) => {
    const previous = getSingleValue(tspanValues, i - 1);
    const labelSize = current.textSize;
    const totalLineHeight = current.fontSize * current.lineHeight;
    const textHeight = Math.ceil(totalLineHeight);
    const padding2 = getSingleValue(backgroundPadding, i);
    const prevPadding = getSingleValue(backgroundPadding, i - 1);
    const xOffset = inline ? dx || 0 : 0;
    const childDy = i && !inline ? previous.fontSize * previous.lineHeight + prevPadding.top + prevPadding.bottom : dy - totalLineHeight * 0.5 - (current.fontSize - current.capHeight);
    return {
      textHeight,
      labelSize,
      heightWithPadding: textHeight + padding2.top + padding2.bottom,
      widthWithPadding: labelSize.width + padding2.left + padding2.right + xOffset,
      y: y2,
      fontSize: current.fontSize,
      dy: childDy
    };
  });
  return textElements.map((textElement, i) => {
    const xCoordinate = getXCoordinate(calculatedProps, textElement.labelSize.width);
    const yCoordinate = textElements.slice(0, i + 1).reduce((prev, curr) => {
      return prev + curr.dy;
    }, y2);
    const padding2 = getSingleValue(backgroundPadding, i);
    const height = textElement.heightWithPadding;
    const xCoord = inline ? getInlineXOffset(calculatedProps, textElements, i) + xCoordinate - padding2.left : xCoordinate;
    const yCoord = inline ? getYCoordinate(calculatedProps, height) - padding2.top : yCoordinate;
    const backgroundProps = {
      key: `tspan-background-${i}`,
      height,
      style: getSingleValue(backgroundStyle, i),
      width: textElement.widthWithPadding,
      transform,
      x: xCoord - padding2.left,
      y: yCoord
    };
    return import_react22.default.cloneElement(backgroundComponent, (0, import_defaults11.default)({}, backgroundComponent.props, backgroundProps));
  });
};
var getBackgroundElement = (calculatedProps, tspanValues) => {
  return shouldUseMultilineBackgrounds(calculatedProps) ? getChildBackgrounds(calculatedProps, tspanValues) : getFullBackground(calculatedProps, tspanValues);
};
var calculateSpanDy = (tspanValues, i, calculatedProps) => {
  const current = getSingleValue(tspanValues, i);
  const previous = getSingleValue(tspanValues, i - 1);
  const previousHeight = previous.fontSize * previous.lineHeight;
  const currentHeight = current.fontSize * current.lineHeight;
  const previousCaps = previous.fontSize - previous.capHeight;
  const currentCaps = current.fontSize - current.capHeight;
  const textHeight = previousHeight - previous.fontSize / 2 + current.fontSize / 2 - previousHeight / 2 + currentHeight / 2 - currentCaps / 2 + previousCaps / 2;
  return shouldUseMultilineBackgrounds(calculatedProps) ? textHeight + current.backgroundPadding.top + previous.backgroundPadding.bottom : textHeight;
};
var getTSpanDy = (tspanValues, calculatedProps, i) => {
  const {
    inline
  } = calculatedProps;
  const current = getSingleValue(tspanValues, i);
  if (i && !inline) {
    return calculateSpanDy(tspanValues, i, calculatedProps);
  } else if (inline) {
    return i === 0 ? current.backgroundPadding.top : void 0;
  }
  return current.backgroundPadding.top;
};
var evaluateProps = (props) => {
  const text = getContent(props.text, props);
  const style = getStyles2(props.style, Object.assign({}, props, {
    text
  }));
  const backgroundStyle = getBackgroundStyles(props.backgroundStyle, Object.assign({}, props, {
    text,
    style
  }));
  const backgroundPadding = getBackgroundPadding(Object.assign({}, props, {
    text,
    style,
    backgroundStyle
  }));
  const id = evaluateProp(props.id, props);
  return Object.assign({}, props, {
    backgroundStyle,
    backgroundPadding,
    style,
    text,
    id
  });
};
var getCalculatedProps = (props) => {
  const ariaLabel = evaluateProp(props.ariaLabel, props);
  const style = getSingleValue(props.style);
  const lineHeight = getLineHeight(props);
  const direction = props.direction ? evaluateProp(props.direction, props) : "inherit";
  const textAnchor = props.textAnchor ? evaluateProp(props.textAnchor, props) : style.textAnchor || "start";
  const verticalAnchor = props.verticalAnchor ? evaluateProp(props.verticalAnchor, props) : style.verticalAnchor || "middle";
  const dx = props.dx ? evaluateProp(props.dx, props) : 0;
  const dy = getDy(props, verticalAnchor, lineHeight);
  const x2 = props.x !== void 0 ? props.x : getPosition2(props, "x");
  const y2 = props.y !== void 0 ? props.y : getPosition2(props, "y");
  const transform = getTransform(props, x2, y2);
  return Object.assign({}, props, {
    ariaLabel,
    lineHeight,
    direction,
    textAnchor,
    verticalAnchor,
    dx,
    dy,
    originalDy: evaluateProp(props.dy, props),
    transform,
    x: x2,
    y: y2
  });
};
var renderLabel = (calculatedProps, tspanValues) => {
  const {
    ariaLabel,
    inline,
    className,
    title,
    events,
    direction,
    text,
    textAnchor,
    dx,
    dy,
    transform,
    x: x2,
    y: y2,
    desc,
    id,
    tabIndex,
    tspanComponent,
    textComponent
  } = calculatedProps;
  const userProps = getSafeUserProps(calculatedProps);
  const textProps = {
    "aria-label": ariaLabel,
    key: "text",
    ...events,
    direction,
    dx,
    x: x2,
    y: y2 + dy,
    transform,
    className,
    title,
    desc: evaluateProp(desc, calculatedProps),
    tabIndex: evaluateProp(tabIndex, calculatedProps),
    id,
    ...userProps
  };
  const tspans = text.map((line, i) => {
    const currentStyle = tspanValues[i].style;
    const tspanProps = {
      key: `${id}-key-${i}`,
      x: !inline ? x2 : void 0,
      dx: inline ? dx + tspanValues[i].backgroundPadding.left : dx,
      dy: getTSpanDy(tspanValues, calculatedProps, i),
      textAnchor: currentStyle.textAnchor || textAnchor,
      style: currentStyle,
      children: line
    };
    return import_react22.default.cloneElement(tspanComponent, tspanProps);
  });
  return import_react22.default.cloneElement(textComponent, textProps, tspans);
};
var defaultProps3 = {
  backgroundComponent: import_react22.default.createElement(Rect, null),
  groupComponent: import_react22.default.createElement("g", null),
  direction: "inherit",
  textComponent: import_react22.default.createElement(Text, null),
  tspanComponent: import_react22.default.createElement(TSpan, null),
  capHeight: 0.71,
  // Magic number from d3.
  lineHeight: 1
};
var VictoryLabel = (initialProps) => {
  const props = evaluateProps((0, import_defaults11.default)({}, initialProps, defaultProps3));
  if (props.text === null || props.text === void 0) {
    return null;
  }
  const calculatedProps = getCalculatedProps(props);
  const {
    text,
    style,
    capHeight,
    backgroundPadding,
    lineHeight
  } = calculatedProps;
  const tspanValues = text.map((line, i) => {
    const currentStyle = getSingleValue(style, i);
    const capHeightPx = convertLengthToPixels(`${capHeight}em`, currentStyle.fontSize);
    const currentLineHeight = getSingleValue(lineHeight, i);
    return {
      style: currentStyle,
      fontSize: currentStyle.fontSize || defaultStyles.fontSize,
      capHeight: capHeightPx,
      text: line,
      // TODO: This looks like a bug:
      textSize: approximateTextSize(line, currentStyle),
      lineHeight: currentLineHeight,
      backgroundPadding: getSingleValue(backgroundPadding, i)
    };
  });
  const label = renderLabel(calculatedProps, tspanValues);
  if (props.backgroundStyle) {
    const backgroundElement = getBackgroundElement(calculatedProps, tspanValues);
    const children = [backgroundElement, label];
    const backgroundWithLabel = import_react22.default.cloneElement(props.groupComponent, {}, children);
    return props.renderInPortal ? import_react22.default.createElement(VictoryPortal, null, backgroundWithLabel) : backgroundWithLabel;
  }
  return props.renderInPortal ? import_react22.default.createElement(VictoryPortal, null, label) : label;
};
VictoryLabel.displayName = "VictoryLabel";
VictoryLabel.role = "label";
VictoryLabel.defaultStyles = defaultStyles;

// node_modules/victory-core/es/victory-clip-container/victory-clip-container.js
var import_uniqueId2 = __toESM(require_uniqueId());
var import_isObject2 = __toESM(require_isObject());
var import_defaults12 = __toESM(require_defaults());
var import_react25 = __toESM(require_react());

// node_modules/victory-core/es/victory-primitives/clip-path.js
var import_react23 = __toESM(require_react());
var ClipPath = (props) => {
  var _a;
  return import_react23.default.createElement("defs", null, import_react23.default.createElement("clipPath", {
    id: (_a = props.clipId) == null ? void 0 : _a.toString()
  }, props.children));
};

// node_modules/victory-core/es/victory-primitives/circle.js
var import_react24 = __toESM(require_react());
function _extends5() {
  _extends5 = Object.assign ? Object.assign.bind() : function(target) {
    for (var i = 1; i < arguments.length; i++) {
      var source = arguments[i];
      for (var key in source) {
        if (Object.prototype.hasOwnProperty.call(source, key)) {
          target[key] = source[key];
        }
      }
    }
    return target;
  };
  return _extends5.apply(this, arguments);
}
var Circle = (0, import_react24.forwardRef)((props, ref) => {
  var _a;
  const {
    desc,
    id,
    tabIndex,
    origin,
    ...rest
  } = props;
  const svgProps = {
    vectorEffect: "non-scaling-stroke",
    id: (_a = evaluateProp(id, props)) == null ? void 0 : _a.toString(),
    tabIndex: evaluateProp(tabIndex, props),
    ...rest
  };
  return desc ? import_react24.default.createElement("circle", _extends5({}, svgProps, {
    ref
  }), import_react24.default.createElement("desc", null, desc)) : import_react24.default.createElement("circle", _extends5({}, svgProps, {
    ref
  }));
});

// node_modules/victory-core/es/victory-clip-container/victory-clip-container.js
var VictoryClipContainer = class extends import_react25.default.Component {
  constructor(props) {
    super(props);
    this.clipId = !(0, import_isObject2.default)(props) || props.clipId === void 0 ? (0, import_uniqueId2.default)("victory-clip-") : props.clipId;
  }
  calculateAttributes(props) {
    const {
      polar,
      origin,
      clipWidth = 0,
      clipHeight = 0,
      translateX = 0,
      translateY = 0
    } = props;
    const clipPadding = getPadding({
      padding: props.clipPadding
    });
    const radius = props.radius || getRadius(props);
    return {
      x: (polar ? origin.x : translateX) - clipPadding.left,
      y: (polar ? origin.y : translateY) - clipPadding.top,
      width: Math.max((polar ? radius : clipWidth) + clipPadding.left + clipPadding.right, 0),
      height: Math.max((polar ? radius : clipHeight) + clipPadding.top + clipPadding.bottom, 0)
    };
  }
  renderClippedGroup(props, clipId) {
    const userProps = getSafeUserProps(props);
    const {
      style,
      events,
      transform,
      children,
      className,
      groupComponent,
      tabIndex
    } = props;
    const clipComponent = this.renderClipComponent(props, clipId);
    const groupProps = Object.assign({
      className,
      style,
      transform,
      key: `clipped-group-${clipId}`,
      clipPath: `url(#${clipId})`
    }, events);
    return import_react25.default.cloneElement(groupComponent, {
      ...groupProps,
      tabIndex,
      ...userProps
    }, [clipComponent, ...import_react25.default.Children.toArray(children)]);
  }
  renderGroup(props) {
    const {
      style,
      events,
      transform,
      children,
      className,
      groupComponent,
      tabIndex
    } = props;
    return import_react25.default.cloneElement(groupComponent, Object.assign({
      className,
      style,
      transform,
      "aria-label": props["aria-label"],
      tabIndex
    }, events), children);
  }
  renderClipComponent(props, clipId) {
    const {
      polar,
      origin,
      clipWidth = 0,
      clipHeight = 0,
      translateX = 0,
      translateY = 0,
      circleComponent,
      rectComponent,
      clipPathComponent
    } = props;
    const {
      top,
      bottom,
      left,
      right
    } = getPadding({
      padding: props.clipPadding
    });
    let child;
    if (polar) {
      const radius = props.radius || getRadius(props);
      const circleProps = {
        r: Math.max(radius + left + right, radius + top + bottom, 0),
        cx: origin.x - left,
        cy: origin.y - top
      };
      child = import_react25.default.cloneElement(circleComponent, circleProps);
    } else {
      const rectProps = {
        x: translateX - left,
        y: translateY - top,
        width: Math.max(clipWidth + left + right, 0),
        height: Math.max(clipHeight + top + bottom, 0)
      };
      child = import_react25.default.cloneElement(rectComponent, rectProps);
    }
    return import_react25.default.cloneElement(clipPathComponent, Object.assign({
      key: `clip-path-${clipId}`
    }, props, {
      clipId
    }), child);
  }
  getClipValue(props, axis) {
    const clipValues = {
      x: props.clipWidth,
      y: props.clipHeight
    };
    if (clipValues[axis] !== void 0) {
      return clipValues[axis];
    }
    const range3 = getRange(props, axis);
    return range3 ? Math.abs(range3[0] - range3[1]) || void 0 : void 0;
  }
  getTranslateValue(props, axis) {
    const translateValues = {
      x: props.translateX,
      y: props.translateY
    };
    if (translateValues[axis] !== void 0) {
      return translateValues[axis];
    }
    const range3 = getRange(props, axis);
    return range3 ? Math.min(...range3) : void 0;
  }
  render() {
    const clipHeight = this.getClipValue(this.props, "y");
    const clipWidth = this.getClipValue(this.props, "x");
    if (clipWidth === void 0 || clipHeight === void 0) {
      return this.renderGroup(this.props);
    }
    const translateX = this.getTranslateValue(this.props, "x");
    const translateY = this.getTranslateValue(this.props, "y");
    const clipProps = (0, import_defaults12.default)({}, this.props, {
      clipHeight,
      clipWidth,
      translateX,
      translateY
    });
    return this.renderClippedGroup(clipProps, this.clipId);
  }
};
__publicField(VictoryClipContainer, "displayName", "VictoryClipContainer");
__publicField(VictoryClipContainer, "role", "container");
__publicField(VictoryClipContainer, "defaultProps", {
  circleComponent: import_react25.default.createElement(Circle, null),
  rectComponent: import_react25.default.createElement(Rect, null),
  clipPathComponent: import_react25.default.createElement(ClipPath, null),
  groupComponent: import_react25.default.createElement("g", null)
});

// node_modules/victory-core/es/victory-theme/grayscale.js
var colors = ["#252525", "#525252", "#737373", "#969696", "#bdbdbd", "#d9d9d9", "#f0f0f0"];
var charcoal = "#252525";
var grey = "#969696";
var sansSerif = "'Gill Sans', 'Seravek', 'Trebuchet MS', sans-serif";
var letterSpacing = "normal";
var fontSize = 14;
var baseProps = {
  width: 450,
  height: 300,
  padding: 50,
  colorScale: colors
};
var baseLabelStyles = {
  fontFamily: sansSerif,
  fontSize,
  letterSpacing,
  padding: 10,
  fill: charcoal,
  stroke: "transparent"
};
var centeredLabelStyles = Object.assign({
  textAnchor: "middle"
}, baseLabelStyles);
var strokeLinecap = "round";
var strokeLinejoin = "round";
var grayscale = {
  area: Object.assign({
    style: {
      data: {
        fill: charcoal
      },
      labels: baseLabelStyles
    }
  }, baseProps),
  axis: Object.assign({
    style: {
      axis: {
        fill: "transparent",
        stroke: charcoal,
        strokeWidth: 1,
        strokeLinecap,
        strokeLinejoin
      },
      axisLabel: Object.assign({}, centeredLabelStyles, {
        padding: 25
      }),
      grid: {
        fill: "none",
        stroke: "none",
        pointerEvents: "painted"
      },
      ticks: {
        fill: "transparent",
        size: 1,
        stroke: "transparent"
      },
      tickLabels: baseLabelStyles
    }
  }, baseProps),
  bar: Object.assign({
    style: {
      data: {
        fill: charcoal,
        padding: 8,
        strokeWidth: 0
      },
      labels: baseLabelStyles
    }
  }, baseProps),
  boxplot: Object.assign({
    style: {
      max: {
        padding: 8,
        stroke: charcoal,
        strokeWidth: 1
      },
      maxLabels: Object.assign({}, baseLabelStyles, {
        padding: 3
      }),
      median: {
        padding: 8,
        stroke: charcoal,
        strokeWidth: 1
      },
      medianLabels: Object.assign({}, baseLabelStyles, {
        padding: 3
      }),
      min: {
        padding: 8,
        stroke: charcoal,
        strokeWidth: 1
      },
      minLabels: Object.assign({}, baseLabelStyles, {
        padding: 3
      }),
      q1: {
        padding: 8,
        fill: grey
      },
      q1Labels: Object.assign({}, baseLabelStyles, {
        padding: 3
      }),
      q3: {
        padding: 8,
        fill: grey
      },
      q3Labels: Object.assign({}, baseLabelStyles, {
        padding: 3
      })
    },
    boxWidth: 20
  }, baseProps),
  candlestick: Object.assign({
    style: {
      data: {
        stroke: charcoal,
        strokeWidth: 1
      },
      labels: Object.assign({}, baseLabelStyles, {
        padding: 5
      })
    },
    candleColors: {
      positive: "#ffffff",
      negative: charcoal
    }
  }, baseProps),
  chart: baseProps,
  errorbar: Object.assign({
    borderWidth: 8,
    style: {
      data: {
        fill: "transparent",
        stroke: charcoal,
        strokeWidth: 2
      },
      labels: baseLabelStyles
    }
  }, baseProps),
  group: Object.assign({
    colorScale: colors
  }, baseProps),
  histogram: Object.assign({
    style: {
      data: {
        fill: grey,
        stroke: charcoal,
        strokeWidth: 2
      },
      labels: baseLabelStyles
    }
  }, baseProps),
  legend: {
    colorScale: colors,
    gutter: 10,
    orientation: "vertical",
    titleOrientation: "top",
    style: {
      data: {
        type: "circle"
      },
      labels: baseLabelStyles,
      title: Object.assign({}, baseLabelStyles, {
        padding: 5
      })
    }
  },
  line: Object.assign({
    style: {
      data: {
        fill: "transparent",
        stroke: charcoal,
        strokeWidth: 2
      },
      labels: baseLabelStyles
    }
  }, baseProps),
  pie: {
    style: {
      data: {
        padding: 10,
        stroke: "transparent",
        strokeWidth: 1
      },
      labels: Object.assign({}, baseLabelStyles, {
        padding: 20
      })
    },
    colorScale: colors,
    width: 400,
    height: 400,
    padding: 50
  },
  scatter: Object.assign({
    style: {
      data: {
        fill: charcoal,
        stroke: "transparent",
        strokeWidth: 0
      },
      labels: baseLabelStyles
    }
  }, baseProps),
  stack: Object.assign({
    colorScale: colors
  }, baseProps),
  tooltip: {
    style: Object.assign({}, baseLabelStyles, {
      padding: 0,
      pointerEvents: "none"
    }),
    flyoutStyle: {
      stroke: charcoal,
      strokeWidth: 1,
      fill: "#f0f0f0",
      pointerEvents: "none"
    },
    flyoutPadding: 5,
    cornerRadius: 5,
    pointerLength: 10
  },
  voronoi: Object.assign({
    style: {
      data: {
        fill: "transparent",
        stroke: "transparent",
        strokeWidth: 0
      },
      labels: Object.assign({}, baseLabelStyles, {
        padding: 5,
        pointerEvents: "none"
      }),
      flyout: {
        stroke: charcoal,
        strokeWidth: 1,
        fill: "#f0f0f0",
        pointerEvents: "none"
      }
    }
  }, baseProps)
};

// node_modules/victory-core/es/victory-theme/material.js
var yellow200 = "#FFF59D";
var deepOrange600 = "#F4511E";
var lime300 = "#DCE775";
var lightGreen500 = "#8BC34A";
var teal700 = "#00796B";
var cyan900 = "#006064";
var colors2 = [deepOrange600, yellow200, lime300, lightGreen500, teal700, cyan900];
var blueGrey50 = "#ECEFF1";
var blueGrey300 = "#90A4AE";
var blueGrey700 = "#455A64";
var grey900 = "#212121";
var sansSerif2 = "'Helvetica Neue', 'Helvetica', sans-serif";
var letterSpacing2 = "normal";
var fontSize2 = 12;
var padding = 8;
var baseProps2 = {
  width: 350,
  height: 350,
  padding: 50
};
var baseLabelStyles2 = {
  fontFamily: sansSerif2,
  fontSize: fontSize2,
  letterSpacing: letterSpacing2,
  padding,
  fill: blueGrey700,
  stroke: "transparent",
  strokeWidth: 0
};
var centeredLabelStyles2 = Object.assign({
  textAnchor: "middle"
}, baseLabelStyles2);
var strokeDasharray = "10, 5";
var strokeLinecap2 = "round";
var strokeLinejoin2 = "round";
var material = {
  area: Object.assign({
    style: {
      data: {
        fill: grey900
      },
      labels: baseLabelStyles2
    }
  }, baseProps2),
  axis: Object.assign({
    style: {
      axis: {
        fill: "transparent",
        stroke: blueGrey300,
        strokeWidth: 2,
        strokeLinecap: strokeLinecap2,
        strokeLinejoin: strokeLinejoin2
      },
      axisLabel: Object.assign({}, centeredLabelStyles2, {
        padding,
        stroke: "transparent"
      }),
      grid: {
        fill: "none",
        stroke: blueGrey50,
        strokeDasharray,
        strokeLinecap: strokeLinecap2,
        strokeLinejoin: strokeLinejoin2,
        pointerEvents: "painted"
      },
      ticks: {
        fill: "transparent",
        size: 5,
        stroke: blueGrey300,
        strokeWidth: 1,
        strokeLinecap: strokeLinecap2,
        strokeLinejoin: strokeLinejoin2
      },
      tickLabels: Object.assign({}, baseLabelStyles2, {
        fill: blueGrey700
      })
    }
  }, baseProps2),
  polarDependentAxis: Object.assign({
    style: {
      ticks: {
        fill: "transparent",
        size: 1,
        stroke: "transparent"
      }
    }
  }),
  bar: Object.assign({
    style: {
      data: {
        fill: blueGrey700,
        padding,
        strokeWidth: 0
      },
      labels: baseLabelStyles2
    }
  }, baseProps2),
  boxplot: Object.assign({
    style: {
      max: {
        padding,
        stroke: blueGrey700,
        strokeWidth: 1
      },
      maxLabels: Object.assign({}, baseLabelStyles2, {
        padding: 3
      }),
      median: {
        padding,
        stroke: blueGrey700,
        strokeWidth: 1
      },
      medianLabels: Object.assign({}, baseLabelStyles2, {
        padding: 3
      }),
      min: {
        padding,
        stroke: blueGrey700,
        strokeWidth: 1
      },
      minLabels: Object.assign({}, baseLabelStyles2, {
        padding: 3
      }),
      q1: {
        padding,
        fill: blueGrey700
      },
      q1Labels: Object.assign({}, baseLabelStyles2, {
        padding: 3
      }),
      q3: {
        padding,
        fill: blueGrey700
      },
      q3Labels: Object.assign({}, baseLabelStyles2, {
        padding: 3
      })
    },
    boxWidth: 20
  }, baseProps2),
  candlestick: Object.assign({
    style: {
      data: {
        stroke: blueGrey700
      },
      labels: Object.assign({}, baseLabelStyles2, {
        padding: 5
      })
    },
    candleColors: {
      positive: "#ffffff",
      negative: blueGrey700
    }
  }, baseProps2),
  chart: baseProps2,
  errorbar: Object.assign({
    borderWidth: 8,
    style: {
      data: {
        fill: "transparent",
        opacity: 1,
        stroke: blueGrey700,
        strokeWidth: 2
      },
      labels: baseLabelStyles2
    }
  }, baseProps2),
  group: Object.assign({
    colorScale: colors2
  }, baseProps2),
  histogram: Object.assign({
    style: {
      data: {
        fill: blueGrey700,
        stroke: grey900,
        strokeWidth: 2
      },
      labels: baseLabelStyles2
    }
  }, baseProps2),
  legend: {
    colorScale: colors2,
    gutter: 10,
    orientation: "vertical",
    titleOrientation: "top",
    style: {
      data: {
        type: "circle"
      },
      labels: baseLabelStyles2,
      title: Object.assign({}, baseLabelStyles2, {
        padding: 5
      })
    }
  },
  line: Object.assign({
    style: {
      data: {
        fill: "transparent",
        opacity: 1,
        stroke: blueGrey700,
        strokeWidth: 2
      },
      labels: baseLabelStyles2
    }
  }, baseProps2),
  pie: Object.assign({
    colorScale: colors2,
    style: {
      data: {
        padding,
        stroke: blueGrey50,
        strokeWidth: 1
      },
      labels: Object.assign({}, baseLabelStyles2, {
        padding: 20
      })
    }
  }, baseProps2),
  scatter: Object.assign({
    style: {
      data: {
        fill: blueGrey700,
        opacity: 1,
        stroke: "transparent",
        strokeWidth: 0
      },
      labels: baseLabelStyles2
    }
  }, baseProps2),
  stack: Object.assign({
    colorScale: colors2
  }, baseProps2),
  tooltip: {
    style: Object.assign({}, baseLabelStyles2, {
      padding: 0,
      pointerEvents: "none"
    }),
    flyoutStyle: {
      stroke: grey900,
      strokeWidth: 1,
      fill: "#f0f0f0",
      pointerEvents: "none"
    },
    flyoutPadding: 5,
    cornerRadius: 5,
    pointerLength: 10
  },
  voronoi: Object.assign({
    style: {
      data: {
        fill: "transparent",
        stroke: "transparent",
        strokeWidth: 0
      },
      labels: Object.assign({}, baseLabelStyles2, {
        padding: 5,
        pointerEvents: "none"
      }),
      flyout: {
        stroke: grey900,
        strokeWidth: 1,
        fill: "#f0f0f0",
        pointerEvents: "none"
      }
    }
  }, baseProps2)
};

// node_modules/victory-core/es/victory-theme/victory-theme.js
var VictoryTheme = {
  grayscale,
  material
};

// node_modules/victory-core/es/victory-primitives/arc.js
var import_defaults13 = __toESM(require_defaults());
var import_react27 = __toESM(require_react());

// node_modules/victory-core/es/victory-primitives/path.js
var import_react26 = __toESM(require_react());
function _extends6() {
  _extends6 = Object.assign ? Object.assign.bind() : function(target) {
    for (var i = 1; i < arguments.length; i++) {
      var source = arguments[i];
      for (var key in source) {
        if (Object.prototype.hasOwnProperty.call(source, key)) {
          target[key] = source[key];
        }
      }
    }
    return target;
  };
  return _extends6.apply(this, arguments);
}
var Path = (0, import_react26.forwardRef)((props, ref) => {
  var _a;
  const {
    desc,
    id,
    tabIndex,
    origin,
    ...rest
  } = props;
  const svgProps = {
    id: (_a = evaluateProp(id, props)) == null ? void 0 : _a.toString(),
    tabIndex: evaluateProp(tabIndex, props),
    ...rest
  };
  return desc ? import_react26.default.createElement("path", _extends6({}, svgProps, {
    ref
  }), import_react26.default.createElement("desc", null, desc)) : import_react26.default.createElement("path", _extends6({}, svgProps, {
    ref
  }));
});

// node_modules/victory-core/es/victory-primitives/arc.js
var getArcPath = (props) => {
  const {
    cx,
    cy,
    r,
    startAngle,
    endAngle,
    closedPath
  } = props;
  const halfAngle = Math.abs(endAngle - startAngle) / 2 + startAngle;
  const x1 = cx + r * Math.cos(degreesToRadians(startAngle));
  const y1 = cy - r * Math.sin(degreesToRadians(startAngle));
  const x2 = cx + r * Math.cos(degreesToRadians(halfAngle));
  const y2 = cy - r * Math.sin(degreesToRadians(halfAngle));
  const x3 = cx + r * Math.cos(degreesToRadians(endAngle));
  const y3 = cy - r * Math.sin(degreesToRadians(endAngle));
  const largerArcFlag1 = halfAngle - startAngle <= 180 ? 0 : 1;
  const largerArcFlag2 = endAngle - halfAngle <= 180 ? 0 : 1;
  const arcStart = closedPath ? ` M ${cx}, ${cy} L ${x1}, ${y1}` : `M ${x1}, ${y1}`;
  const arc1 = `A ${r}, ${r}, 0, ${largerArcFlag1}, 0, ${x2}, ${y2}`;
  const arc2 = `A ${r}, ${r}, 0, ${largerArcFlag2}, 0, ${x3}, ${y3}`;
  const arcEnd = closedPath ? "Z" : "";
  return `${arcStart} ${arc1} ${arc2} ${arcEnd}`;
};
var evaluateProps2 = (props) => {
  const ariaLabel = evaluateProp(props.ariaLabel, props);
  const desc = evaluateProp(props.desc, props);
  const id = evaluateProp(props.id, props);
  const style = evaluateStyle(Object.assign({
    stroke: "black",
    fill: "none"
  }, props.style), props);
  const tabIndex = evaluateProp(props.tabIndex, props);
  return Object.assign({}, props, {
    ariaLabel,
    desc,
    id,
    style,
    tabIndex
  });
};
var defaultProps4 = {
  pathComponent: import_react27.default.createElement(Path, null),
  role: "presentation",
  shapeRendering: "auto"
};
var Arc = (initialProps) => {
  const props = evaluateProps2((0, import_defaults13.default)({}, initialProps, defaultProps4));
  return import_react27.default.cloneElement(props.pathComponent, {
    ...props.events,
    "aria-label": props.ariaLabel,
    d: getArcPath(props),
    style: props.style,
    desc: props.desc,
    tabIndex: props.tabIndex,
    className: props.className,
    role: props.role,
    shapeRendering: props.shapeRendering,
    transform: props.transform,
    clipPath: props.clipPath
  });
};

// node_modules/victory-core/es/victory-primitives/background.js
var import_defaults14 = __toESM(require_defaults());
var import_react28 = __toESM(require_react());
var evaluateProps3 = (props) => {
  const id = evaluateProp(props.id, props);
  return Object.assign({}, props, {
    id
  });
};
var defaultProps5 = {
  circleComponent: import_react28.default.createElement(Circle, null),
  rectComponent: import_react28.default.createElement(Rect, null),
  role: "presentation",
  shapeRendering: "auto"
};
var Background = (initialProps) => {
  const props = evaluateProps3((0, import_defaults14.default)({}, initialProps, defaultProps5));
  return props.polar ? import_react28.default.cloneElement(props.circleComponent, {
    ...props.events,
    style: props.style,
    role: props.role,
    shapeRendering: props.shapeRendering,
    cx: props.x,
    cy: props.y,
    r: props.height,
    className: props.className
  }) : import_react28.default.cloneElement(props.rectComponent, {
    ...props.events,
    style: props.style,
    role: props.role,
    shapeRendering: props.shapeRendering,
    x: props.x,
    y: props.y,
    rx: props.rx,
    ry: props.ry,
    width: props.width,
    height: props.height,
    className: props.className
  });
};

// node_modules/victory-core/es/victory-primitives/border.js
var import_defaults15 = __toESM(require_defaults());
var import_react29 = __toESM(require_react());
var evaluateProps4 = (props) => {
  const ariaLabel = evaluateProp(props.ariaLabel, props);
  const desc = evaluateProp(props.desc, props);
  const id = evaluateProp(props.id, props);
  const style = evaluateStyle(Object.assign({
    fill: "none"
  }, props.style), props);
  const tabIndex = evaluateProp(props.tabIndex, props);
  return Object.assign({}, props, {
    ariaLabel,
    desc,
    id,
    style,
    tabIndex
  });
};
var defaultProps6 = {
  rectComponent: import_react29.default.createElement(Rect, null),
  role: "presentation",
  shapeRendering: "auto"
};
var Border = (initialProps) => {
  const props = evaluateProps4((0, import_defaults15.default)({}, initialProps, defaultProps6));
  return import_react29.default.cloneElement(props.rectComponent, {
    ...props.events,
    "aria-label": props.ariaLabel,
    style: props.style,
    desc: props.desc,
    tabIndex: props.tabIndex,
    transform: props.transform,
    className: props.className,
    role: props.role,
    shapeRendering: props.shapeRendering,
    x: props.x,
    y: props.y,
    width: props.width,
    height: props.height,
    clipPath: props.clipPath
  });
};

// node_modules/victory-core/es/victory-primitives/line.js
var import_react30 = __toESM(require_react());
function _extends7() {
  _extends7 = Object.assign ? Object.assign.bind() : function(target) {
    for (var i = 1; i < arguments.length; i++) {
      var source = arguments[i];
      for (var key in source) {
        if (Object.prototype.hasOwnProperty.call(source, key)) {
          target[key] = source[key];
        }
      }
    }
    return target;
  };
  return _extends7.apply(this, arguments);
}
var Line = (0, import_react30.forwardRef)((props, ref) => {
  var _a;
  const {
    desc,
    id,
    tabIndex,
    origin,
    ...rest
  } = props;
  const svgProps = {
    vectorEffect: "non-scaling-stroke",
    id: (_a = evaluateProp(id, props)) == null ? void 0 : _a.toString(),
    tabIndex: evaluateProp(tabIndex, props),
    ...rest
  };
  return desc ? import_react30.default.createElement("line", _extends7({}, svgProps, {
    ref
  }), import_react30.default.createElement("desc", null, desc)) : import_react30.default.createElement("line", _extends7({}, svgProps, {
    ref
  }));
});

// node_modules/victory-core/es/victory-primitives/line-segment.js
var import_defaults16 = __toESM(require_defaults());
var import_react31 = __toESM(require_react());
var evaluateProps5 = (props) => {
  const ariaLabel = evaluateProp(props.ariaLabel, props);
  const desc = evaluateProp(props.desc, props);
  const id = evaluateProp(props.id, props);
  const style = evaluateStyle(Object.assign({
    stroke: "black"
  }, props.style), props);
  const tabIndex = evaluateProp(props.tabIndex, props);
  return Object.assign({}, props, {
    ariaLabel,
    desc,
    id,
    style,
    tabIndex
  });
};
var defaultProps7 = {
  lineComponent: import_react31.default.createElement(Line, null),
  role: "presentation",
  shapeRendering: "auto"
};
var LineSegment = (initialProps) => {
  const props = evaluateProps5((0, import_defaults16.default)({}, initialProps, defaultProps7));
  return import_react31.default.cloneElement(props.lineComponent, {
    ...props.events,
    "aria-label": props.ariaLabel,
    style: props.style,
    desc: props.desc,
    tabIndex: props.tabIndex,
    className: props.className,
    role: props.role,
    shapeRendering: props.shapeRendering,
    x1: props.x1,
    x2: props.x2,
    y1: props.y1,
    y2: props.y2,
    transform: props.transform,
    clipPath: props.clipPath
  });
};

// node_modules/victory-core/es/victory-primitives/point.js
var import_defaults17 = __toESM(require_defaults());
var import_react32 = __toESM(require_react());
var getPath = (props) => {
  const {
    x: x2,
    y: y2,
    size,
    symbol
  } = props;
  if (props.getPath) {
    return props.getPath(x2, y2, size);
  }
  const pathFunctions = point_path_helpers_exports;
  const symbolFunction = typeof pathFunctions[symbol] === "function" ? pathFunctions[symbol] : pathFunctions.circle;
  return symbolFunction(x2, y2, size);
};
var evaluateProps6 = (props) => {
  const ariaLabel = evaluateProp(props.ariaLabel, props);
  const desc = evaluateProp(props.desc, props);
  const id = evaluateProp(props.id, props);
  const size = evaluateProp(props.size, props);
  const style = evaluateStyle(props.style, props);
  const symbol = evaluateProp(props.symbol, props);
  const tabIndex = evaluateProp(props.tabIndex, props);
  return Object.assign({}, props, {
    ariaLabel,
    desc,
    id,
    size,
    style,
    symbol,
    tabIndex
  });
};
var defaultProps8 = {
  pathComponent: import_react32.default.createElement(Path, null),
  role: "presentation",
  shapeRendering: "auto"
};
var Point = (initialProps) => {
  const props = evaluateProps6((0, import_defaults17.default)({}, initialProps, defaultProps8));
  const userProps = getSafeUserProps(props);
  return import_react32.default.cloneElement(props.pathComponent, {
    ...props.events,
    "aria-label": props.ariaLabel,
    d: getPath(props),
    style: props.style,
    desc: props.desc,
    tabIndex: props.tabIndex,
    role: props.role,
    shapeRendering: props.shapeRendering,
    className: props.className,
    transform: props.transform,
    clipPath: props.clipPath,
    ...userProps
  });
};

// node_modules/victory-core/es/victory-primitives/whisker.js
var import_defaults18 = __toESM(require_defaults());
var import_react33 = __toESM(require_react());
var evaluateProps7 = (props) => {
  const ariaLabel = evaluateProp(props.ariaLabel, props);
  const desc = evaluateProp(props.desc, props);
  const id = evaluateProp(props.id, props);
  const style = evaluateStyle(props.style, props);
  const tabIndex = evaluateProp(props.tabIndex, props);
  return Object.assign({}, props, {
    ariaLabel,
    desc,
    id,
    style,
    tabIndex
  });
};
var defaultProps9 = {
  groupComponent: import_react33.default.createElement("g", null),
  lineComponent: import_react33.default.createElement(Line, null),
  role: "presentation",
  shapeRendering: "auto"
};
var Whisker = (initialProps) => {
  const props = evaluateProps7((0, import_defaults18.default)({}, initialProps, defaultProps9));
  const {
    ariaLabel,
    groupComponent,
    lineComponent,
    events,
    className,
    majorWhisker,
    minorWhisker,
    transform,
    clipPath,
    role,
    shapeRendering,
    style,
    desc,
    tabIndex
  } = props;
  const baseProps3 = {
    ...events,
    style,
    desc,
    tabIndex,
    className,
    transform,
    clipPath,
    role,
    shapeRendering
  };
  return import_react33.default.cloneElement(groupComponent, {}, [import_react33.default.cloneElement(lineComponent, Object.assign({
    key: "major-whisker",
    "aria-label": ariaLabel
  }, baseProps3, majorWhisker)), import_react33.default.cloneElement(lineComponent, Object.assign({
    key: "minor-whisker",
    "aria-label": ariaLabel
  }, baseProps3, minorWhisker))]);
};

// node_modules/victory-area/es/helper-methods.js
var getDataWithBaseline = (props, scale) => {
  let data = data_exports.getData(props);
  if (data.length < 2) {
    data = [];
  }
  const getDefaultMin = (axis) => {
    const defaultZero = scale_exports.getType(scale[axis]) === "log" ? 1 / Number.MAX_SAFE_INTEGER : 0;
    const domain = scale[axis].domain();
    const minY = collection_exports.getMinValue(domain);
    const maxY = collection_exports.getMaxValue(domain);
    let defaultMin = defaultZero;
    if (minY < 0 && maxY <= 0) {
      defaultMin = maxY;
    } else if (minY >= 0 && maxY > 0) {
      defaultMin = minY;
    }
    return collection_exports.containsDates(domain) ? new Date(defaultMin) : defaultMin;
  };
  return data.map((datum) => {
    const _y1 = datum._y1 !== void 0 ? datum._y1 : datum._y;
    const _y0 = datum._y0 !== void 0 ? datum._y0 : getDefaultMin("y");
    const _x1 = datum._x1 !== void 0 ? datum._x1 : datum._x;
    const _x0 = datum._x0 !== void 0 ? datum._x0 : getDefaultMin("x");
    return Object.assign({}, datum, {
      _y0,
      _y1,
      _x0,
      _x1
    });
  });
};
var getCalculatedValues = (props) => {
  const {
    polar
  } = props;
  const defaultStyles2 = helpers_exports.getDefaultStyles(props, "area");
  const style = helpers_exports.getStyles(props.style, defaultStyles2);
  const range3 = {
    x: helpers_exports.getRange(props, "x"),
    y: helpers_exports.getRange(props, "y")
  };
  const domain = {
    x: domain_exports.getDomainWithZero(props, "x"),
    y: domain_exports.getDomainWithZero(props, "y")
  };
  const scale = {
    x: scale_exports.getBaseScale(props, "x").domain(domain.x).range(props.horizontal ? range3.y : range3.x),
    y: scale_exports.getBaseScale(props, "y").domain(domain.y).range(props.horizontal ? range3.x : range3.y)
  };
  const origin = polar ? props.origin || helpers_exports.getPolarOrigin(props) : void 0;
  const data = getDataWithBaseline(props, scale);
  return {
    style,
    data,
    scale,
    domain,
    origin
  };
};
var getBaseProps = (initialProps, fallbackProps22) => {
  const modifiedProps = helpers_exports.modifyProps(initialProps, fallbackProps22, "area");
  const props = Object.assign({}, modifiedProps, getCalculatedValues(modifiedProps));
  const {
    data,
    domain,
    events,
    groupComponent,
    height,
    horizontal,
    interpolation,
    origin,
    padding: padding2,
    polar,
    scale,
    sharedEvents,
    standalone,
    style,
    theme,
    width,
    labels,
    name,
    disableInlineStyles
  } = props;
  const initialChildProps = {
    parent: {
      style: style.parent,
      width,
      height,
      scale,
      data,
      domain,
      standalone,
      theme,
      polar,
      origin,
      padding: padding2,
      name,
      horizontal
    },
    all: {
      data: {
        horizontal,
        polar,
        origin,
        scale,
        data,
        interpolation,
        groupComponent,
        style: disableInlineStyles ? {} : style.data,
        disableInlineStyles
      }
    }
  };
  return data.reduce((childProps, datum, index) => {
    const text = label_helpers_exports.getText(props, datum, index);
    if (text !== void 0 && text !== null || labels && (events || sharedEvents)) {
      const eventKey = !helpers_exports.isNil(datum.eventKey) ? datum.eventKey : index;
      childProps[eventKey] = {
        labels: label_helpers_exports.getProps(props, index)
      };
    }
    return childProps;
  }, initialChildProps);
};

// node_modules/victory-area/es/area.js
var import_defaults19 = __toESM(require_defaults());
var import_react34 = __toESM(require_react());
var defined2 = (d) => {
  const y2 = d._y1 !== void 0 ? d._y1 : d._y;
  return y2 !== null && y2 !== void 0 && d._y0 !== null;
};
var getXAccessor2 = (scale) => {
  return (d) => scale.x(d._x1 !== void 0 ? d._x1 : d._x);
};
var getYAccessor2 = (scale) => {
  return (d) => scale.y(d._y1 !== void 0 ? d._y1 : d._y);
};
var getY0Accessor = (scale) => {
  return (d) => scale.y(d._y0);
};
var getAngleAccessor2 = (scale) => {
  return (d) => {
    const x2 = scale.x(d._x1 !== void 0 ? d._x1 : d._x);
    return -1 * x2 + Math.PI / 2;
  };
};
var getCartesianArea = (props) => {
  const {
    horizontal,
    scale
  } = props;
  const interpolationFunction = line_helpers_exports.getInterpolationFunction(props);
  return horizontal ? area_default().defined(defined2).curve(interpolationFunction).x0(getY0Accessor(scale)).x1(getYAccessor2(scale)).y(getXAccessor2(scale)) : area_default().defined(defined2).curve(interpolationFunction).x(getXAccessor2(scale)).y1(getYAccessor2(scale)).y0(getY0Accessor(scale));
};
var getAreaFunction = (props) => {
  const {
    polar,
    scale
  } = props;
  const interpolationFunction = line_helpers_exports.getInterpolationFunction(props);
  return polar ? areaRadial_default().defined(defined2).curve(interpolationFunction).angle(getAngleAccessor2(scale)).outerRadius(getYAccessor2(scale)).innerRadius(getY0Accessor(scale)) : getCartesianArea(props);
};
var evaluateProps8 = (props) => {
  const ariaLabel = helpers_exports.evaluateProp(props.ariaLabel, props);
  const desc = helpers_exports.evaluateProp(props.desc, props);
  const id = helpers_exports.evaluateProp(props.id, props);
  const style = helpers_exports.evaluateStyle(Object.assign({
    fill: "black"
  }, props.style), props);
  const tabIndex = helpers_exports.evaluateProp(props.tabIndex, props);
  return Object.assign({}, props, {
    ariaLabel,
    desc,
    id,
    style,
    tabIndex
  });
};
var defaultProps10 = {
  groupComponent: import_react34.default.createElement("g", null),
  pathComponent: import_react34.default.createElement(Path, null),
  role: "presentation",
  shapeRendering: "auto"
};
var Area = (initialProps) => {
  const props = evaluateProps8((0, import_defaults19.default)({}, initialProps, defaultProps10));
  const {
    ariaLabel,
    role,
    shapeRendering,
    className,
    polar,
    origin,
    data,
    pathComponent,
    events,
    groupComponent,
    clipPath,
    id,
    style,
    desc,
    tabIndex
  } = props;
  const userProps = user_props_exports.getSafeUserProps(props);
  const defaultTransform = polar && origin ? `translate(${origin.x}, ${origin.y})` : void 0;
  const transform = props.transform || defaultTransform;
  const renderLine = style.stroke && style.stroke !== "none" && style.stroke !== "transparent";
  const areaFunction = getAreaFunction(props);
  const lineFunction = renderLine && line_helpers_exports.getLineFunction(props);
  const areaStroke = style.stroke ? "none" : style.fill;
  const sharedProps = {
    "aria-label": ariaLabel,
    className,
    role,
    shapeRendering,
    transform,
    ...events,
    clipPath,
    tabIndex
  };
  const area = import_react34.default.cloneElement(pathComponent, Object.assign({
    key: `${id}-area`,
    style: Object.assign({}, style, {
      stroke: areaStroke
    }),
    d: areaFunction(data),
    desc,
    tabIndex
  }, sharedProps, userProps));
  const line = renderLine ? import_react34.default.cloneElement(pathComponent, Object.assign({
    key: `${id}-area-stroke`,
    style: Object.assign({}, style, {
      fill: "none"
    }),
    d: lineFunction(data)
  }, sharedProps)) : null;
  return renderLine ? import_react34.default.cloneElement(groupComponent, userProps, [area, line]) : area;
};

// node_modules/victory-area/es/victory-area.js
var fallbackProps = {
  width: 450,
  height: 300,
  padding: 50,
  interpolation: "linear"
};
var options = {
  components: [{
    name: "parent",
    index: "parent"
  }, {
    name: "data",
    index: "all"
  }, {
    name: "labels"
  }]
};
var _VictoryAreaBase = class _VictoryAreaBase extends import_react35.default.Component {
  static getBaseProps(props) {
    return getBaseProps(props, fallbackProps);
  }
  // Overridden in native versions
  shouldAnimate() {
    return !!this.props.animate;
  }
  render() {
    const {
      animationWhitelist,
      role
    } = _VictoryAreaBase;
    const props = helpers_exports.modifyProps(this.props, fallbackProps, role);
    if (this.shouldAnimate()) {
      return this.animateComponent(props, animationWhitelist);
    }
    const children = this.renderContinuousData(props);
    const component = props.standalone ? this.renderContainer(props.containerComponent, children) : children;
    return user_props_exports.withSafeUserProps(component, props);
  }
};
__publicField(_VictoryAreaBase, "animationWhitelist", ["data", "domain", "height", "padding", "style", "width"]);
__publicField(_VictoryAreaBase, "defaultProps", {
  containerComponent: import_react35.default.createElement(VictoryContainer, null),
  dataComponent: import_react35.default.createElement(Area, null),
  groupComponent: import_react35.default.createElement(VictoryClipContainer, null),
  labelComponent: import_react35.default.createElement(VictoryLabel, {
    renderInPortal: true
  }),
  samples: 50,
  sortKey: "x",
  sortOrder: "ascending",
  standalone: true,
  theme: VictoryTheme.grayscale
});
__publicField(_VictoryAreaBase, "displayName", "VictoryArea");
__publicField(_VictoryAreaBase, "role", "area");
__publicField(_VictoryAreaBase, "continuous", true);
__publicField(_VictoryAreaBase, "defaultTransitions", default_transitions_exports.continuousTransitions());
__publicField(_VictoryAreaBase, "defaultPolarTransitions", default_transitions_exports.continuousPolarTransitions());
__publicField(_VictoryAreaBase, "getDomain", domain_exports.getDomainWithZero);
__publicField(_VictoryAreaBase, "getData", data_exports.getData);
__publicField(_VictoryAreaBase, "expectedComponents", ["dataComponent", "labelComponent", "groupComponent", "containerComponent"]);
var VictoryAreaBase = _VictoryAreaBase;
var VictoryArea = addEvents(VictoryAreaBase, options);

// node_modules/victory-axis/es/victory-axis.js
var import_isEmpty5 = __toESM(require_isEmpty());
var import_react36 = __toESM(require_react());

// node_modules/victory-axis/es/helper-methods.js
var import_defaults20 = __toESM(require_defaults());
var orientationSign = {
  top: -1,
  left: -1,
  right: 1,
  bottom: 1
};
var exists = (val) => val !== null && val !== void 0;
var getCurrentAxis2 = (props, axis) => {
  const {
    orientation,
    horizontal
  } = props;
  if (orientation) {
    const dimensions = {
      top: "x",
      bottom: "x",
      left: "y",
      right: "y"
    };
    return dimensions[orientation];
  }
  const otherAxis = axis === "x" ? "y" : "x";
  return horizontal ? otherAxis : axis;
};
var getScale2 = (props) => {
  const axis = axis_exports.getAxis(props);
  const currentAxis = getCurrentAxis2(props, axis);
  const scale = scale_exports.getBaseScale(props, axis);
  const propsDomain = props.domain && props.domain[axis];
  const domain = propsDomain || axis_exports.getDomain(props) || scale.domain();
  scale.range(helpers_exports.getRange(props, currentAxis));
  scale.domain(domain);
  return scale;
};
var getStyleObject = (props) => {
  const {
    theme,
    dependentAxis
  } = props;
  const generalAxisStyle = theme && theme.axis && theme.axis.style;
  const axisType = dependentAxis ? "dependentAxis" : "independentAxis";
  const specificAxisStyle = theme && theme[axisType] && theme[axisType].style;
  const mergeStyles = () => {
    const styleNamespaces = ["axis", "axisLabel", "grid", "parent", "tickLabels", "ticks"];
    return styleNamespaces.reduce((memo, curr) => {
      memo[curr] = (0, import_defaults20.default)({}, specificAxisStyle[curr], generalAxisStyle[curr]);
      return memo;
    }, {});
  };
  return generalAxisStyle && specificAxisStyle ? mergeStyles() : specificAxisStyle || generalAxisStyle;
};
var getStyles3 = function(props, styleObject) {
  if (styleObject === void 0) {
    styleObject = {};
  }
  const style = props.style || {};
  const parentStyleProps = {
    height: "100%",
    width: "100%"
  };
  return {
    parent: (0, import_defaults20.default)(style.parent, styleObject.parent, parentStyleProps),
    axis: (0, import_defaults20.default)({}, style.axis, styleObject.axis),
    axisLabel: (0, import_defaults20.default)({}, style.axisLabel, styleObject.axisLabel),
    grid: (0, import_defaults20.default)({}, style.grid, styleObject.grid),
    ticks: (0, import_defaults20.default)({}, style.ticks, styleObject.ticks),
    tickLabels: (0, import_defaults20.default)({}, style.tickLabels, styleObject.tickLabels)
  };
};
var getTickProps = (layout, style, datum) => {
  const {
    position,
    transform
  } = layout;
  return {
    x1: transform.x,
    y1: transform.y,
    x2: transform.x + position.x2,
    y2: transform.y + position.y2,
    style,
    datum
  };
};
var getTickLabelProps = (layout, style, anchors, datum, text) => {
  const {
    position,
    transform
  } = layout;
  return {
    style,
    x: transform.x + position.x,
    y: transform.y + position.y,
    verticalAnchor: anchors.verticalAnchor,
    textAnchor: anchors.textAnchor,
    angle: style.angle,
    text,
    datum
  };
};
var getGridProps = (layout, style, datum) => {
  const {
    edge,
    transform
  } = layout;
  return {
    x1: transform.x,
    y1: transform.y,
    x2: edge.x + transform.x,
    y2: edge.y + transform.y,
    style,
    datum
  };
};
var getAxisProps = (modifiedProps, calculatedValues, globalTransform) => {
  const {
    style,
    padding: padding2,
    isVertical: isVertical2
  } = calculatedValues;
  const {
    width,
    height
  } = modifiedProps;
  return {
    style: style.axis,
    x1: isVertical2 ? globalTransform.x : padding2.left + globalTransform.x,
    x2: isVertical2 ? globalTransform.x : width - padding2.right + globalTransform.x,
    y1: isVertical2 ? padding2.top + globalTransform.y : globalTransform.y,
    y2: isVertical2 ? height - padding2.bottom + globalTransform.y : globalTransform.y
  };
};
var getEvaluatedStyles = (style, props) => {
  return {
    tickStyle: helpers_exports.evaluateStyle(style.ticks, props),
    labelStyle: helpers_exports.evaluateStyle(style.tickLabels, props),
    gridStyle: helpers_exports.evaluateStyle(style.grid, props)
  };
};
var getAxisLabelProps = (props, calculatedValues, globalTransform) => {
  const {
    style,
    orientation,
    padding: padding2,
    labelPadding,
    isVertical: isVertical2
  } = calculatedValues;
  const sign = orientationSign[orientation];
  const hPadding = padding2.left + padding2.right;
  const vPadding = padding2.top + padding2.bottom;
  const verticalAnchor = sign < 0 ? "end" : "start";
  const labelStyle = style.axisLabel;
  const angle = isVertical2 ? -90 : 0;
  const x2 = isVertical2 ? globalTransform.x + sign * labelPadding : (props.width - hPadding) / 2 + padding2.left + globalTransform.x;
  const y2 = isVertical2 ? (props.height - vPadding) / 2 + padding2.top + globalTransform.y : sign * labelPadding + globalTransform.y;
  return {
    x: x2,
    y: y2,
    verticalAnchor: labelStyle.verticalAnchor || verticalAnchor,
    textAnchor: labelStyle.textAnchor || "middle",
    angle: labelStyle.angle === void 0 ? angle : labelStyle.angle,
    style: labelStyle,
    text: props.label
  };
};
var getAnchors = (orientation, isVertical2) => {
  const anchorOrientation = {
    top: "end",
    left: "end",
    right: "start",
    bottom: "start"
  };
  const anchor = anchorOrientation[orientation];
  return {
    textAnchor: isVertical2 ? anchor : "middle",
    verticalAnchor: isVertical2 ? "middle" : anchor
  };
};
var getLabelPadding = (props, style) => {
  const labelStyle = style.axisLabel || {};
  if (labelStyle.padding !== void 0 && labelStyle.padding !== null) {
    return labelStyle.padding;
  }
  const isVertical2 = axis_exports.isVertical(props);
  const fontSize3 = labelStyle.fontSize || 14;
  return props.label ? fontSize3 * (isVertical2 ? 2.3 : 1.6) : 0;
};
var getDefaultOrientations = (axis, originSign, horizontal) => {
  const sign = originSign || "positive";
  const orientations = {
    positive: {
      x: "bottom",
      y: "left"
    },
    negative: {
      x: "top",
      y: "right"
    }
  };
  const horizontalOrientations = {
    positive: {
      x: "left",
      y: "bottom"
    },
    negative: {
      x: "right",
      y: "top"
    }
  };
  return horizontal ? horizontalOrientations[sign][axis] : orientations[sign][axis];
};
var getStandaloneOffset = (props, calculatedValues) => {
  const {
    style,
    scale,
    orientation,
    padding: padding2,
    axis,
    ticks: ticks2,
    stringTicks: stringTicks2,
    isVertical: isVertical2,
    labelPadding
  } = calculatedValues;
  const {
    polar,
    horizontal
  } = props;
  const sharedProps = {
    scale: {
      [axis]: scale
    },
    polar,
    horizontal,
    ticks: ticks2,
    stringTicks: stringTicks2
  };
  const xPadding = orientation === "right" ? padding2.right : padding2.left;
  const yPadding = orientation === "top" ? padding2.top : padding2.bottom;
  const offsetX = props.offsetX !== null && props.offsetX !== void 0 ? props.offsetX : xPadding;
  const offsetY = props.offsetY !== null && props.offsetY !== void 0 ? props.offsetY : yPadding;
  const fontSize3 = style.axisLabel.fontSize || 14;
  const tickSizes = ticks2.map((data, index) => {
    const tick = stringTicks2 ? props.tickValues[data - 1] : data;
    const tickStyle = helpers_exports.evaluateStyle(style.ticks, Object.assign({}, sharedProps, {
      tick,
      index
    }));
    return tickStyle.size || 0;
  });
  const totalPadding = fontSize3 + 2 * Math.max(...tickSizes) + labelPadding;
  const minimumPadding = 1.2 * fontSize3;
  const x2 = isVertical2 ? totalPadding : minimumPadding;
  const y2 = isVertical2 ? minimumPadding : totalPadding;
  return {
    x: offsetX !== null && offsetX !== void 0 ? offsetX : x2,
    y: offsetY !== null && offsetY !== void 0 ? offsetY : y2
  };
};
var isEqual3 = (a, b) => {
  if (a instanceof Date && b instanceof Date) {
    return a.getTime() === b.getTime();
  }
  return a === b;
};
var getOffset2 = (props, calculatedValues) => {
  const {
    scale,
    origin,
    orientation,
    orientations,
    domain,
    padding: padding2
  } = calculatedValues;
  const {
    top,
    bottom,
    left,
    right
  } = padding2;
  const calculatedOrientation = {
    x: orientation === "bottom" || orientation === "top" ? orientation : orientations.x,
    y: orientation === "left" || orientation === "right" ? orientation : orientations.y
  };
  const orientationOffset = {
    x: calculatedOrientation.y === "left" ? left : right,
    y: calculatedOrientation.x === "bottom" ? bottom : top
  };
  const originOffset = {
    x: calculatedOrientation.y === "left" ? 0 : props.width,
    y: calculatedOrientation.x === "bottom" ? props.height : 0
  };
  const originPosition = {
    x: isEqual3(origin.x, domain.x[0]) || isEqual3(origin.x, domain.x[1]) ? 0 : scale.x(origin.x),
    y: isEqual3(origin.y, domain.y[0]) || isEqual3(origin.y, domain.y[1]) ? 0 : scale.y(origin.y)
  };
  const x2 = originPosition.x ? Math.abs(originOffset.x - originPosition.x) : orientationOffset.x;
  const y2 = originPosition.y ? Math.abs(originOffset.y - originPosition.y) : orientationOffset.y;
  const offsetX = exists(props.offsetX) ? props.offsetX : x2;
  const offsetY = exists(props.offsetY) ? props.offsetY : y2;
  return {
    x: offsetX,
    y: offsetY
  };
};
var getHorizontalOffset = (props, calculatedValues) => {
  const {
    scale,
    origin,
    orientation,
    orientations,
    domain,
    padding: padding2
  } = calculatedValues;
  const {
    top,
    bottom,
    left,
    right
  } = padding2;
  const calculatedOrientation = {
    y: orientation === "bottom" || orientation === "top" ? orientation : orientations.x,
    x: orientation === "left" || orientation === "right" ? orientation : orientations.y
  };
  const orientationOffset = {
    x: calculatedOrientation.y === "bottom" ? bottom : top,
    y: calculatedOrientation.x === "left" ? left : right
  };
  const originOffset = {
    y: calculatedOrientation.x === "left" ? 0 : props.width,
    x: calculatedOrientation.y === "bottom" ? props.height : 0
  };
  const originPosition = {
    x: isEqual3(origin.x, domain.x[0]) || isEqual3(origin.x, domain.x[1]) ? 0 : scale.x(origin.x),
    y: isEqual3(origin.y, domain.y[0]) || isEqual3(origin.y, domain.y[1]) ? 0 : scale.y(origin.y)
  };
  const y2 = originPosition.x ? Math.abs(originOffset.x - originPosition.x) : orientationOffset.x;
  const x2 = originPosition.y ? Math.abs(originOffset.y - originPosition.y) : orientationOffset.y;
  const offsetX = exists(props.offsetX) ? props.offsetX : x2;
  const offsetY = exists(props.offsetY) ? props.offsetY : y2;
  return {
    x: offsetX,
    y: offsetY
  };
};
var getTransform2 = (props, calculatedValues, offset) => {
  const {
    orientation,
    axis
  } = calculatedValues;
  const axisValue = axis_exports.getAxisValue(props, axis);
  return {
    top: {
      x: 0,
      y: axisValue !== void 0 ? axisValue : offset.y
    },
    bottom: {
      x: 0,
      y: axisValue !== void 0 ? axisValue : props.height - offset.y
    },
    left: {
      x: axisValue !== void 0 ? axisValue : offset.x,
      y: 0
    },
    right: {
      x: axisValue !== void 0 ? axisValue : props.width - offset.x,
      y: 0
    }
  }[orientation];
};
var getTickPosition = (style, orientation, isVertical2) => {
  const {
    tickStyle,
    labelStyle
  } = style;
  const size = tickStyle.size || 0;
  const tickPadding = tickStyle.padding || 0;
  const labelPadding = labelStyle.padding || 0;
  const tickSpacing = size + tickPadding + labelPadding;
  const sign = orientationSign[orientation];
  return {
    x: isVertical2 ? sign * tickSpacing : 0,
    x2: isVertical2 ? sign * size : 0,
    y: isVertical2 ? 0 : sign * tickSpacing,
    y2: isVertical2 ? 0 : sign * size
  };
};
var getTickTransform = (tick, globalTransform, isVertical2) => {
  return {
    x: isVertical2 ? globalTransform.x : tick + globalTransform.x,
    y: isVertical2 ? tick + globalTransform.y : globalTransform.y
  };
};
var getGridEdge = (props, calculatedValues) => {
  const {
    orientation,
    padding: padding2,
    isVertical: isVertical2
  } = calculatedValues;
  const sign = -orientationSign[orientation];
  const x2 = isVertical2 ? sign * (props.width - (padding2.left + padding2.right)) : 0;
  const y2 = isVertical2 ? 0 : sign * (props.height - (padding2.top + padding2.bottom));
  return {
    x: x2,
    y: y2
  };
};
var getGridOffset = (calculatedValues, offset) => {
  const {
    padding: padding2,
    orientation,
    crossAxis
  } = calculatedValues;
  const xPadding = orientation === "right" ? padding2.right : padding2.left;
  const yPadding = orientation === "top" ? padding2.top : padding2.bottom;
  return {
    x: crossAxis ? offset.x - xPadding : 0,
    y: crossAxis ? offset.y - yPadding : 0
  };
};
var getLayoutProps = (modifiedProps, calculatedValues) => {
  let offset;
  if (calculatedValues.domain.x && calculatedValues.domain.y) {
    offset = modifiedProps.horizontal ? getHorizontalOffset(modifiedProps, calculatedValues) : getOffset2(modifiedProps, calculatedValues);
  } else {
    offset = getStandaloneOffset(modifiedProps, calculatedValues);
  }
  return {
    globalTransform: getTransform2(modifiedProps, calculatedValues, offset),
    gridOffset: getGridOffset(calculatedValues, offset),
    gridEdge: getGridEdge(modifiedProps, calculatedValues)
  };
};
var getOrientation = (props) => {
  if (props.orientation) {
    return props.orientation;
  }
  const defaultOrientations = {
    dependent: props.horizontal ? "bottom" : "left",
    independent: props.horizontal ? "left" : "bottom"
  };
  return props.dependentAxis ? defaultOrientations.dependent : defaultOrientations.independent;
};
var getCalculatedValues2 = (props) => {
  const defaultStyles2 = getStyleObject(props);
  const style = getStyles3(props, defaultStyles2);
  const padding2 = helpers_exports.getPadding(props);
  const labelPadding = getLabelPadding(props, style);
  const stringTicks2 = axis_exports.stringTicks(props) ? props.tickValues : void 0;
  const axis = axis_exports.getAxis(props);
  const axisDomain = axis_exports.getDomain(props);
  const axisScale = getScale2(props);
  const xAxisDomain = axis === "x" ? axisDomain : void 0;
  const yAxisDomain = axis === "y" ? axisDomain : void 0;
  const xAxisScale = axis === "x" ? axisScale : void 0;
  const yAxisScale = axis === "y" ? axisScale : void 0;
  const crossAxis = !(props.crossAxis === false || props.standalone === true);
  const ticks2 = axis_exports.getTicks(props, axisScale, crossAxis);
  const tickFormat2 = axis_exports.getTickFormat(props, axisScale);
  const range3 = {
    x: helpers_exports.getRange(props, "x"),
    y: helpers_exports.getRange(props, "y")
  };
  const domain = {
    x: props.domain && props.domain.x ? props.domain.x : xAxisDomain,
    y: props.domain && props.domain.y ? props.domain.y : yAxisDomain
  };
  const scale = {
    x: props.domain && props.domain.x ? scale_exports.getBaseScale(props, "x").domain(props.domain.x).range(props.horizontal ? range3.y : range3.x) : xAxisScale,
    y: props.domain && props.domain.y ? scale_exports.getBaseScale(props, "y").domain(props.domain.y).range(props.horizontal ? range3.x : range3.y) : yAxisScale
  };
  const origin = domain.x && domain.y ? axis_exports.getOrigin(domain) : void 0;
  const originSign = origin ? {
    x: axis_exports.getOriginSign(origin.x, domain.x),
    y: axis_exports.getOriginSign(origin.y, domain.y)
  } : void 0;
  const orientations = originSign ? {
    x: getDefaultOrientations("x", originSign.y, props.horizontal),
    y: getDefaultOrientations("y", originSign.x, props.horizontal)
  } : void 0;
  const orientation = orientations ? props.orientation || orientations[axis] : getOrientation(props);
  const isVertical2 = axis_exports.isVertical(Object.assign({}, props, {
    orientation
  }));
  const anchors = getAnchors(orientation, isVertical2);
  return {
    anchors,
    axis,
    crossAxis,
    domain,
    isVertical: isVertical2,
    labelPadding,
    orientation,
    orientations,
    origin,
    padding: padding2,
    scale,
    stringTicks: stringTicks2,
    style,
    tickFormat: tickFormat2,
    ticks: ticks2
  };
};
var getBaseProps2 = (initialProps, fallbackProps22) => {
  const props = axis_exports.modifyProps(initialProps, fallbackProps22);
  const calculatedValues = getCalculatedValues2(props);
  const {
    axis,
    style,
    orientation,
    isVertical: isVertical2,
    scale,
    ticks: ticks2,
    tickFormat: tickFormat2,
    anchors,
    domain,
    stringTicks: stringTicks2
  } = calculatedValues;
  const otherAxis = axis === "x" ? "y" : "x";
  const {
    width,
    height,
    standalone,
    theme,
    polar,
    padding: padding2,
    horizontal
  } = props;
  const {
    globalTransform,
    gridOffset,
    gridEdge
  } = getLayoutProps(props, calculatedValues);
  const sharedProps = {
    scale: {
      [axis]: scale[axis]
    },
    polar,
    horizontal,
    ticks: ticks2,
    stringTicks: stringTicks2
  };
  const axisProps = getAxisProps(props, calculatedValues, globalTransform);
  const axisLabelProps = getAxisLabelProps(props, calculatedValues, globalTransform);
  const initialChildProps = {
    parent: Object.assign({
      style: style.parent,
      ticks: ticks2,
      standalone,
      theme,
      width,
      height,
      padding: padding2,
      domain
    }, sharedProps)
  };
  const gridProps = {
    dimension: otherAxis,
    range: {
      [otherAxis]: helpers_exports.getRange(props, otherAxis)
    },
    scale: props.scale && props.scale[otherAxis] ? {
      [otherAxis]: props.scale[otherAxis]
    } : void 0
  };
  return ticks2.reduce((childProps, tickValue, index) => {
    var _a, _b, _c;
    const tick = stringTicks2 ? stringTicks2[index] : tickValue;
    const text = tickFormat2(tickValue, index, ticks2);
    const styles = getEvaluatedStyles(style, Object.assign({}, sharedProps, {
      tick,
      tickValue,
      index,
      text
    }));
    const tickLayout = {
      position: getTickPosition(styles, orientation, isVertical2),
      transform: getTickTransform((_a = scale[axis]) == null ? void 0 : _a.call(scale, tickValue), globalTransform, isVertical2)
    };
    const gridLayout = {
      edge: gridEdge,
      transform: {
        x: isVertical2 ? -gridOffset.x + globalTransform.x : ((_b = scale[axis]) == null ? void 0 : _b.call(scale, tickValue)) + globalTransform.x,
        y: isVertical2 ? ((_c = scale[axis]) == null ? void 0 : _c.call(scale, tickValue)) + globalTransform.y : gridOffset.y + globalTransform.y
      }
    };
    childProps[index] = {
      axis: Object.assign({
        dimension: axis
      }, sharedProps, axisProps),
      axisLabel: Object.assign({}, sharedProps, axisLabelProps),
      ticks: Object.assign({}, sharedProps, getTickProps(tickLayout, styles.tickStyle, tickValue)),
      tickLabels: Object.assign({}, sharedProps, getTickLabelProps(tickLayout, styles.labelStyle, anchors, tickValue, text)),
      grid: Object.assign({}, sharedProps, gridProps, getGridProps(gridLayout, styles.gridStyle, tickValue))
    };
    return childProps;
  }, initialChildProps);
};

// node_modules/victory-axis/es/victory-axis.js
var fallbackProps2 = {
  width: 450,
  height: 300,
  padding: 50
};
var options2 = {
  components: [{
    name: "axis",
    index: 0
  }, {
    name: "axisLabel",
    index: 0
  }, {
    name: "grid"
  }, {
    name: "parent",
    index: "parent"
  }, {
    name: "ticks"
  }, {
    name: "tickLabels"
  }]
};
var VictoryAxisBase = class extends import_react36.default.Component {
  static getStyles(props) {
    return getStyles3(props);
  }
  static getBaseProps(props) {
    return getBaseProps2(props, fallbackProps2);
  }
  renderLine(props) {
    const {
      axisComponent
    } = props;
    const axisProps = this.getComponentProps(axisComponent, "axis", 0);
    return import_react36.default.cloneElement(axisComponent, axisProps);
  }
  renderLabel(props) {
    const {
      axisLabelComponent,
      label
    } = props;
    if (!label) {
      return null;
    }
    const axisLabelProps = this.getComponentProps(axisLabelComponent, "axisLabel", 0);
    return import_react36.default.cloneElement(axisLabelComponent, axisLabelProps);
  }
  renderGridAndTicks(props) {
    const {
      tickComponent,
      tickLabelComponent,
      gridComponent,
      name
    } = props;
    const shouldRender = (componentProps) => {
      const {
        style = {},
        events = {}
      } = componentProps;
      const visible = style.stroke !== "transparent" && style.stroke !== "none" && style.strokeWidth !== 0;
      return visible || !(0, import_isEmpty5.default)(events);
    };
    return this.dataKeys.map((key, index) => {
      const tickProps = this.getComponentProps(tickComponent, "ticks", index);
      const BaseTickComponent = import_react36.default.cloneElement(tickComponent, tickProps);
      const TickComponent = shouldRender(BaseTickComponent.props) ? BaseTickComponent : void 0;
      const gridProps = this.getComponentProps(gridComponent, "grid", index);
      const BaseGridComponent = import_react36.default.cloneElement(gridComponent, gridProps);
      const GridComponent = shouldRender(BaseGridComponent.props) ? BaseGridComponent : void 0;
      const tickLabelProps = this.getComponentProps(tickLabelComponent, "tickLabels", index);
      const TickLabel = import_react36.default.cloneElement(tickLabelComponent, tickLabelProps);
      const children = [GridComponent, TickComponent, TickLabel].filter(Boolean);
      return import_react36.default.cloneElement(props.groupComponent, {
        key: `${name}-tick-group-${key}`
      }, children);
    });
  }
  fixLabelOverlap(gridAndTicks, props) {
    const isVertical2 = axis_exports.isVertical(props);
    const size = isVertical2 ? props.height : props.width;
    const isVictoryLabel = (child) => child.type && child.type.role === "label";
    const labels = gridAndTicks.map((gridAndTick) => gridAndTick.props.children).reduce((accumulator, childArr) => accumulator.concat(childArr), []).filter(isVictoryLabel).map((child) => child.props);
    const paddingToObject = (padding2) => typeof padding2 === "object" ? Object.assign({}, {
      top: 0,
      right: 0,
      bottom: 0,
      left: 0
    }, padding2) : {
      top: padding2,
      right: padding2,
      bottom: padding2,
      left: padding2
    };
    const labelsSumSize = labels.reduce((sum2, label) => {
      const padding2 = paddingToObject(label.style.padding);
      const labelSize = textsize_exports.approximateTextSize(label.text, {
        angle: label.angle,
        fontSize: label.style.fontSize,
        letterSpacing: label.style.letterSpacing,
        fontFamily: label.style.fontFamily
      });
      return sum2 + (isVertical2 ? labelSize.height + padding2.top + padding2.bottom : labelSize.width + padding2.right + padding2.left);
    }, 0);
    const availiableLabelCount = Math.floor(size * gridAndTicks.length / labelsSumSize);
    const divider = Math.ceil(gridAndTicks.length / availiableLabelCount) || 1;
    const getLabelCoord = (gridAndTick) => gridAndTick.props.children.filter(isVictoryLabel).reduce((prev, child) => (isVertical2 ? child.props.y : child.props.x) || 0, 0);
    const sorted = gridAndTicks.sort(
      (a, b) => isVertical2 ? getLabelCoord(b) - getLabelCoord(a) : getLabelCoord(a) - getLabelCoord(b)
      // ordinary axis has left-right orientation
    );
    return sorted.filter((gridAndTick, index) => index % divider === 0);
  }
  // Overridden in native versions
  shouldAnimate() {
    return !!this.props.animate;
  }
  render() {
    const {
      animationWhitelist
    } = VictoryAxis;
    const props = axis_exports.modifyProps(this.props, fallbackProps2);
    const userProps = user_props_exports.getSafeUserProps(this.props);
    if (this.shouldAnimate()) {
      return this.animateComponent(props, animationWhitelist);
    }
    const gridAndTicks = this.renderGridAndTicks(props);
    const modifiedGridAndTicks = props.fixLabelOverlap ? this.fixLabelOverlap(gridAndTicks, props) : gridAndTicks;
    const children = [this.renderLine(props), this.renderLabel(props), ...modifiedGridAndTicks];
    const container = import_react36.default.cloneElement(props.containerComponent, userProps);
    return props.standalone ? this.renderContainer(container, children) : import_react36.default.cloneElement(props.groupComponent, userProps, children);
  }
};
__publicField(VictoryAxisBase, "animationWhitelist", ["style", "domain", "range", "tickCount", "tickValues", "offsetX", "offsetY", "padding", "width", "height"]);
__publicField(VictoryAxisBase, "displayName", "VictoryAxis");
__publicField(VictoryAxisBase, "role", "axis");
__publicField(VictoryAxisBase, "defaultTransitions", {
  onExit: {
    duration: 500
  },
  onEnter: {
    duration: 500
  }
});
__publicField(VictoryAxisBase, "defaultProps", {
  axisComponent: import_react36.default.createElement(LineSegment, null),
  axisLabelComponent: import_react36.default.createElement(VictoryLabel, null),
  tickLabelComponent: import_react36.default.createElement(VictoryLabel, null),
  tickComponent: import_react36.default.createElement(LineSegment, null),
  gridComponent: import_react36.default.createElement(LineSegment, null),
  standalone: true,
  theme: VictoryTheme.grayscale,
  containerComponent: import_react36.default.createElement(VictoryContainer, null),
  groupComponent: import_react36.default.createElement("g", {
    role: "presentation"
  }),
  fixLabelOverlap: false
});
__publicField(VictoryAxisBase, "getDomain", axis_exports.getDomain);
__publicField(VictoryAxisBase, "getAxis", axis_exports.getAxis);
__publicField(VictoryAxisBase, "expectedComponents", ["axisComponent", "axisLabelComponent", "groupComponent", "containerComponent", "tickComponent", "tickLabelComponent", "gridComponent"]);
var VictoryAxis = addEvents(VictoryAxisBase, options2);

// node_modules/victory-bar/es/victory-bar.js
var import_react38 = __toESM(require_react());

// node_modules/victory-bar/es/helper-methods.js
var getBarPosition = (props, datum) => {
  const getDefaultMin = (axis) => {
    const defaultZero = scale_exports.getType(props.scale[axis]) === "log" ? 1 / Number.MAX_SAFE_INTEGER : 0;
    let defaultMin = defaultZero;
    const minY = collection_exports.getMinValue(props.domain[axis]);
    const maxY = collection_exports.getMaxValue(props.domain[axis]);
    if (minY < 0 && maxY <= 0) {
      defaultMin = maxY;
    } else if (minY >= 0 && maxY > 0) {
      defaultMin = minY;
    }
    return datum[`_${axis}`] instanceof Date ? new Date(defaultMin) : defaultMin;
  };
  const _y0 = datum._y0 !== void 0 ? datum._y0 : getDefaultMin("y");
  const _x0 = datum._x0 !== void 0 ? datum._x0 : getDefaultMin("x");
  return helpers_exports.scalePoint(props, Object.assign({}, datum, {
    _y0,
    _x0
  }));
};
var getCalculatedValues3 = (props) => {
  const {
    polar
  } = props;
  const defaultStyles2 = helpers_exports.getDefaultStyles(props, "bar");
  const style = !props.disableInlineStyles ? helpers_exports.getStyles(props.style, defaultStyles2) : {};
  const range3 = props.range || {
    x: helpers_exports.getRange(props, "x"),
    y: helpers_exports.getRange(props, "y")
  };
  const domain = {
    x: domain_exports.getDomainWithZero(props, "x"),
    y: domain_exports.getDomainWithZero(props, "y")
  };
  const scale = {
    x: scale_exports.getBaseScale(props, "x").domain(domain.x).range(props.horizontal ? range3.y : range3.x),
    y: scale_exports.getBaseScale(props, "y").domain(domain.y).range(props.horizontal ? range3.x : range3.y)
  };
  const origin = polar ? props.origin || helpers_exports.getPolarOrigin(props) : void 0;
  let data = data_exports.getData(props);
  data = data_exports.formatDataFromDomain(data, domain, 0);
  return {
    style,
    data,
    scale,
    domain,
    origin
  };
};
var getBaseProps3 = (initialProps, fallbackProps22) => {
  const modifiedProps = helpers_exports.modifyProps(initialProps, fallbackProps22, "bar");
  const props = Object.assign({}, modifiedProps, getCalculatedValues3(modifiedProps));
  const {
    alignment,
    barRatio,
    cornerRadius,
    data,
    disableInlineStyles,
    domain,
    events,
    height,
    horizontal,
    origin,
    padding: padding2,
    polar,
    scale,
    sharedEvents,
    standalone,
    style,
    theme,
    width,
    labels,
    name,
    barWidth,
    getPath: getPath4
  } = props;
  const initialChildProps = {
    parent: {
      horizontal,
      domain,
      scale,
      width,
      height,
      data,
      standalone,
      name,
      theme,
      polar,
      origin,
      padding: padding2,
      style: style.parent
    }
  };
  return data.reduce((childProps, datum, index) => {
    const eventKey = !helpers_exports.isNil(datum.eventKey) ? datum.eventKey : index;
    const {
      x: x2,
      y: y2,
      y0,
      x0
    } = getBarPosition(props, datum);
    const dataProps = {
      alignment,
      barRatio,
      barWidth,
      cornerRadius,
      data,
      datum,
      disableInlineStyles,
      getPath: getPath4,
      horizontal,
      index,
      polar,
      origin,
      scale,
      style: style.data,
      width,
      height,
      x: x2,
      y: y2,
      y0,
      x0
    };
    childProps[eventKey] = {
      data: dataProps
    };
    const text = label_helpers_exports.getText(props, datum, index);
    if (text !== void 0 && text !== null || labels && (events || sharedEvents)) {
      childProps[eventKey].labels = label_helpers_exports.getProps(props, index);
    }
    return childProps;
  }, initialChildProps);
};

// node_modules/victory-bar/es/bar.js
var import_defaults21 = __toESM(require_defaults());
var import_react37 = __toESM(require_react());

// node_modules/victory-bar/es/bar-helper-methods.js
var import_isPlainObject6 = __toESM(require_isPlainObject());
var DEFAULT_BAR_WIDTH = 8;
var getBarWidth = (barWidth, props) => {
  const {
    scale,
    data,
    style
  } = props;
  if (barWidth) {
    return helpers_exports.evaluateProp(barWidth, props);
  } else if (style.width) {
    return style.width;
  }
  const range3 = scale.x.range();
  const extent2 = Math.abs(range3[1] - range3[0]);
  const bars = data.length + 2;
  const barRatio = props.barRatio || 0.5;
  const defaultWidth = barRatio * (data.length < 2 ? DEFAULT_BAR_WIDTH : extent2 / bars);
  return Math.max(1, defaultWidth);
};
var getCornerRadiusFromObject = (cornerRadius, props) => {
  const realCornerRadius = {
    topLeft: 0,
    topRight: 0,
    bottomLeft: 0,
    bottomRight: 0
  };
  const updateCornerRadius = (corner, fallback) => {
    if (!helpers_exports.isNil(cornerRadius[corner])) {
      realCornerRadius[corner] = helpers_exports.evaluateProp(cornerRadius[corner], props);
    } else if (!helpers_exports.isNil(cornerRadius[fallback])) {
      realCornerRadius[corner] = helpers_exports.evaluateProp(cornerRadius[fallback], props);
    }
  };
  updateCornerRadius("topLeft", "top");
  updateCornerRadius("topRight", "top");
  updateCornerRadius("bottomLeft", "bottom");
  updateCornerRadius("bottomRight", "bottom");
  return realCornerRadius;
};
function isCornerRadiusObject(cornerRadius) {
  return (0, import_isPlainObject6.default)(cornerRadius);
}
var getCornerRadius = (cornerRadius, props) => {
  const realCornerRadius = {
    topLeft: 0,
    topRight: 0,
    bottomLeft: 0,
    bottomRight: 0
  };
  if (!cornerRadius) {
    return realCornerRadius;
  }
  if (isCornerRadiusObject(cornerRadius)) {
    return getCornerRadiusFromObject(cornerRadius, props);
  }
  realCornerRadius.topLeft = helpers_exports.evaluateProp(cornerRadius, props);
  realCornerRadius.topRight = helpers_exports.evaluateProp(cornerRadius, props);
  return realCornerRadius;
};
var getStyle2 = function(style, props) {
  if (style === void 0) {
    style = {};
  }
  if (props.disableInlineStyles) {
    return {};
  }
  const stroke = style.fill || "black";
  const baseStyle = {
    fill: "black",
    stroke
  };
  return helpers_exports.evaluateStyle(Object.assign(baseStyle, style), props);
};

// node_modules/victory-bar/es/geometry-helper-methods.js
var point2 = (x2, y2) => ({
  x: x2,
  y: y2,
  distance(p1) {
    return Math.sqrt(Math.pow(this.x - p1.x, 2) + Math.pow(this.y - p1.y, 2));
  },
  // vector addition in 2d plane
  add(p1) {
    return point2(this.x + p1.x, this.y + p1.y);
  },
  // vector subtraction in 2d
  // returns p0 - p1
  subtract(p1) {
    return point2(this.x - p1.x, this.y - p1.y);
  },
  // multiply a 2d point by a scalar
  scalarMult(n) {
    return point2(this.x * n, this.y * n);
  },
  scalarDivide(n) {
    if (n === 0) {
      throw new Error("Division by 0 error");
    }
    return point2(this.x / n, this.y / n);
  },
  equals(p1) {
    return this.x === p1.x && this.y === p1.y;
  }
});
var circle2 = (center, radius) => ({
  center,
  radius,
  hasIntersection(circle1) {
    const P0 = this.center;
    const P1 = circle1.center;
    const r0 = this.radius;
    const r1 = circle1.radius;
    const d = P0.distance(P1);
    if (d > r0 + r1) {
      return false;
    }
    if (d < Math.abs(r0 - r1)) {
      return false;
    }
    return true;
  },
  equals(circle1) {
    const P0 = this.center;
    const P1 = circle1.center;
    const r0 = this.radius;
    const r1 = circle1.radius;
    return r0 === r1 && P0.equals(P1);
  },
  // Source: http://paulbourke.net/geometry/circlesphere/
  // "Intersection of two circles" by Paul Bourke
  // Left-most point is returned as 0th element of array
  // Right-most point is returned as 1st elemennt of array
  intersection(circle1) {
    const P0 = this.center;
    const P1 = circle1.center;
    const r0 = this.radius;
    const r1 = circle1.radius;
    const d = P0.distance(P1);
    if (!this.hasIntersection(circle1) || this.equals(circle1)) {
      return [];
    }
    const a = (Math.pow(r0, 2) - Math.pow(r1, 2) + Math.pow(d, 2)) / (2 * d);
    const h = Math.sqrt(Math.pow(r0, 2) - Math.pow(a, 2));
    const P2 = P0.add(P1.subtract(P0).scalarMult(a).scalarDivide(d));
    const {
      x: x0,
      y: y0
    } = P0;
    const {
      x: x1,
      y: y1
    } = P1;
    const {
      x: x2,
      y: y2
    } = P2;
    const P3s = [point2(x2 - h * (y1 - y0) / d, y2 + h * (x1 - x0) / d), point2(x2 + h * (y1 - y0) / d, y2 - h * (x1 - x0) / d)];
    P3s.sort((Point1, Point2) => Point1.x - Point2.x);
    return P3s;
  },
  solveX(y2) {
    const sqrt2 = Math.sqrt(Math.pow(this.radius, 2) - Math.pow(y2 - this.center.y, 2));
    return [this.center.x - sqrt2, this.center.x + sqrt2];
  },
  solveY(x2) {
    const sqrt2 = Math.sqrt(Math.pow(this.radius, 2) - Math.pow(x2 - this.center.x, 2));
    return [this.center.y - sqrt2, this.center.y + sqrt2];
  }
});

// node_modules/victory-bar/es/path-helper-methods.js
var getPosition3 = (props, width) => {
  const {
    x: x2,
    x0,
    y: y2,
    y0,
    horizontal
  } = props;
  const alignment = props.alignment || "middle";
  const size = alignment === "middle" ? width / 2 : width;
  const sign = horizontal ? -1 : 1;
  if (horizontal) {
    return {
      x0,
      x1: x2,
      y0: alignment === "start" ? y2 : y2 - sign * size,
      y1: alignment === "end" ? y2 : y2 + sign * size
    };
  }
  return {
    x0: alignment === "start" ? x2 : x2 - sign * size,
    x1: alignment === "end" ? x2 : x2 + sign * size,
    y0,
    y1: y2
  };
};
var getAngle2 = (props, index) => {
  const {
    data,
    scale
  } = props;
  const x2 = data[index]._x1 === void 0 ? "_x" : "_x1";
  return scale.x(data[index][x2]);
};
var getAngularWidth = (props, width) => {
  const {
    scale
  } = props;
  const range3 = scale.y.range();
  const r = Math.max(...range3);
  const angularRange = Math.abs(scale.x.range()[1] - scale.x.range()[0]);
  return width / (2 * Math.PI * r) * angularRange;
};
var transformAngle = (angle) => {
  return -1 * angle + Math.PI / 2;
};
var getCustomBarPath = (props, width) => {
  const {
    getPath: getPath4
  } = props;
  if (typeof getPath4 === "function") {
    const propsWithCalculatedValues = {
      ...props,
      ...getPosition3(props, width)
    };
    return getPath4(propsWithCalculatedValues);
  }
};
var getStartAngle = (props, index) => {
  const {
    data,
    scale,
    alignment
  } = props;
  const currentAngle = getAngle2(props, index);
  const angularRange = Math.abs(scale.x.range()[1] - scale.x.range()[0]);
  const previousAngle = index === 0 ? getAngle2(props, data.length - 1) - Math.PI * 2 : getAngle2(props, index - 1);
  if (index === 0 && angularRange < 2 * Math.PI) {
    return scale.x.range()[0];
  } else if (alignment === "start" || alignment === "end") {
    return alignment === "start" ? previousAngle : currentAngle;
  }
  return (currentAngle + previousAngle) / 2;
};
var getEndAngle = (props, index) => {
  const {
    data,
    scale,
    alignment
  } = props;
  const currentAngle = getAngle2(props, index);
  const angularRange = Math.abs(scale.x.range()[1] - scale.x.range()[0]);
  const lastAngle = scale.x.range()[1] === 2 * Math.PI ? getAngle2(props, 0) + Math.PI * 2 : scale.x.range()[1];
  const nextAngle = index === data.length - 1 ? getAngle2(props, 0) + Math.PI * 2 : getAngle2(props, index + 1);
  if (index === data.length - 1 && angularRange < 2 * Math.PI) {
    return lastAngle;
  } else if (alignment === "start" || alignment === "end") {
    return alignment === "start" ? currentAngle : nextAngle;
  }
  return (currentAngle + nextAngle) / 2;
};
var mapPointsToPath = (coords, cornerRadius, direction) => {
  const topLeftPath = `${cornerRadius.topLeft} ${cornerRadius.topLeft} ${direction}`;
  const topRightPath = `${cornerRadius.topRight} ${cornerRadius.topRight} ${direction}`;
  const bottomLeftPath = `${cornerRadius.bottomLeft} ${cornerRadius.bottomLeft} ${direction}`;
  const bottomRightPath = `${cornerRadius.bottomRight} ${cornerRadius.bottomRight} ${direction}`;
  const commands = ["M", `A ${bottomLeftPath},`, "L", `A ${topLeftPath},`, "L", `A ${topRightPath},`, "L", `A ${bottomRightPath},`];
  const path = commands.reduce((acc, command, i) => `${acc}${command} ${coords[i].x}, ${coords[i].y} 
`, "");
  return `${path} z`;
};
var getVerticalBarPoints = (position, sign, cr) => {
  const {
    x0,
    x1,
    y0,
    y1
  } = position;
  const getHalfPoints = (side) => {
    const isLeft = side === "Left";
    const signL = isLeft ? 1 : -1;
    const x2 = isLeft ? x0 : x1;
    let bottomPoint = {
      x: x2 + signL * cr[`bottom${side}`],
      y: y0
    };
    let bottomMiddlePoint = {
      x: x2,
      y: y0 - sign * cr[`bottom${side}`]
    };
    let topMiddlePoint = {
      x: x2,
      y: y1 + sign * cr[`top${side}`]
    };
    let topPoint = {
      x: x2 + signL * cr[`top${side}`],
      y: y1
    };
    const hasIntersection = sign === 1 ? y0 - cr[`bottom${side}`] < y1 + cr[`top${side}`] : y0 + cr[`bottom${side}`] > y1 - cr[`top${side}`];
    if (hasIntersection) {
      const topCenter = point2(x2 + signL * cr[`top${side}`], y1 + sign * cr[`top${side}`]);
      const topCircle = circle2(topCenter, cr[`top${side}`]);
      const bottomCenter = point2(x2 + signL * cr[`bottom${side}`], y0 - sign * cr[`bottom${side}`]);
      const bottomCircle = circle2(bottomCenter, cr[`bottom${side}`]);
      const circleIntersection = topCircle.intersection(bottomCircle);
      const hasArcIntersection = circleIntersection.length > 0;
      if (hasArcIntersection) {
        const arcIntersection = circleIntersection[isLeft ? 0 : 1];
        bottomMiddlePoint = {
          x: arcIntersection.x,
          y: arcIntersection.y
        };
        topMiddlePoint = {
          x: arcIntersection.x,
          y: arcIntersection.y
        };
      } else {
        const hasBottomLineTopArcIntersection = cr[`top${side}`] > cr[`bottom${side}`];
        if (hasBottomLineTopArcIntersection) {
          const newX = topCircle.solveX(y0)[isLeft ? 0 : 1];
          bottomPoint = {
            x: newX,
            y: y0
          };
          bottomMiddlePoint = {
            x: newX,
            y: y0
          };
          topMiddlePoint = {
            x: newX,
            y: y0
          };
        } else {
          const newX = bottomCircle.solveX(y1)[isLeft ? 0 : 1];
          bottomMiddlePoint = {
            x: newX,
            y: y1
          };
          topMiddlePoint = {
            x: newX,
            y: y1
          };
          topPoint = {
            x: newX,
            y: y1
          };
        }
      }
    }
    const points = [bottomPoint, bottomMiddlePoint, topMiddlePoint, topPoint];
    return isLeft ? points : points.reverse();
  };
  return getHalfPoints("Left").concat(getHalfPoints("Right"));
};
var getHorizontalBarPoints = (position, sign, cr) => {
  const {
    y0,
    y1
  } = position;
  const x0 = position.x0 < position.x1 ? position.x0 : position.x1;
  const x1 = position.x0 < position.x1 ? position.x1 : position.x0;
  const getHalfPoints = (side) => {
    const isTop = side === "top";
    const signL = isTop ? -1 : 1;
    const y2 = isTop ? y1 : y0;
    let leftPoint = {
      x: x0,
      y: y2 - signL * cr[`${side}Left`]
    };
    let leftMiddlePoint = {
      x: x0 + cr[`${side}Left`],
      y: y2
    };
    let rightMiddlePoint = {
      x: x1 - cr[`${side}Right`],
      y: y2
    };
    let rightPoint = {
      x: x1,
      y: y2 - signL * cr[`${side}Right`]
    };
    const hasIntersection = leftMiddlePoint.x > rightMiddlePoint.x;
    if (hasIntersection) {
      const leftCenter = point2(x0 + cr[`${side}Left`], y2 - signL * cr[`${side}Left`]);
      const leftCircle = circle2(leftCenter, cr[`${side}Left`]);
      const rightCenter = point2(x1 - cr[`${side}Right`], y2 - signL * cr[`${side}Right`]);
      const rightCircle = circle2(rightCenter, cr[`${side}Right`]);
      const circleIntersection = leftCircle.intersection(rightCircle);
      const hasArcIntersection = circleIntersection.length > 0;
      if (hasArcIntersection) {
        const arcIntersection = circleIntersection[sign > 0 ? 1 : 0];
        leftMiddlePoint = {
          x: arcIntersection.x,
          y: arcIntersection.y
        };
        rightMiddlePoint = {
          x: arcIntersection.x,
          y: arcIntersection.y
        };
      } else {
        const hasLeftLineRightArcIntersection = cr[`${side}Right`] > cr[`${side}Left`];
        if (hasLeftLineRightArcIntersection) {
          const newY = rightCircle.solveY(x0)[isTop ? 0 : 1];
          leftPoint = {
            x: x0,
            y: newY
          };
          leftMiddlePoint = {
            x: x0,
            y: newY
          };
          rightMiddlePoint = {
            x: x0,
            y: newY
          };
        } else {
          const newY = leftCircle.solveY(x1)[isTop ? 0 : 1];
          rightPoint = {
            x: x1,
            y: newY
          };
          rightMiddlePoint = {
            x: x1,
            y: newY
          };
          leftMiddlePoint = {
            x: x1,
            y: newY
          };
        }
      }
    }
    return [leftPoint, leftMiddlePoint, rightMiddlePoint, rightPoint];
  };
  const topPoints = getHalfPoints("top");
  const bottomPoints = getHalfPoints("bottom");
  return [
    bottomPoints[1],
    bottomPoints[0],
    ...topPoints,
    // eslint-disable-next-line no-magic-numbers
    bottomPoints[3],
    bottomPoints[2]
  ];
};
var getVerticalBarPath = (props, width, cornerRadius) => {
  const position = getPosition3(props, width);
  const sign = position.y0 > position.y1 ? 1 : -1;
  const direction = sign > 0 ? "0 0 1" : "0 0 0";
  const points = getVerticalBarPoints(position, sign, cornerRadius);
  return mapPointsToPath(points, cornerRadius, direction);
};
var getHorizontalBarPath = (props, width, cornerRadius) => {
  const position = getPosition3(props, width);
  const sign = position.x0 < position.x1 ? 1 : -1;
  const direction = "0 0 1";
  const cr = {
    topRight: sign > 0 ? cornerRadius.topLeft : cornerRadius.bottomLeft,
    bottomRight: sign > 0 ? cornerRadius.topRight : cornerRadius.bottomRight,
    bottomLeft: sign > 0 ? cornerRadius.bottomRight : cornerRadius.topRight,
    topLeft: sign > 0 ? cornerRadius.bottomLeft : cornerRadius.topLeft
  };
  const points = getHorizontalBarPoints(position, sign, cr);
  return mapPointsToPath(points, cr, direction);
};
var getVerticalPolarBarPath = (props, cornerRadius) => {
  const {
    datum,
    scale,
    index,
    alignment,
    style
  } = props;
  const r1 = scale.y(datum._y0 || 0);
  const r2 = scale.y(datum._y1 !== void 0 ? datum._y1 : datum._y);
  const currentAngle = scale.x(datum._x1 !== void 0 ? datum._x1 : datum._x);
  let start;
  let end;
  if (style.width) {
    const width = getAngularWidth(props, style.width);
    const size = alignment === "middle" ? width / 2 : width;
    start = alignment === "start" ? currentAngle : currentAngle - size;
    end = alignment === "end" ? currentAngle : currentAngle + size;
  } else {
    start = getStartAngle(props, Number(index));
    end = getEndAngle(props, Number(index));
  }
  const getPath4 = (edge) => {
    const pathFunction = arc_default().innerRadius(r1).outerRadius(r2).startAngle(transformAngle(start)).endAngle(transformAngle(end)).cornerRadius(cornerRadius[edge]);
    return pathFunction();
  };
  const getPathData = (edge) => {
    const rightPath = getPath4(`${edge}Right`);
    const rightMoves = rightPath.match(/[A-Z]/g) || [];
    const rightCoords = rightPath.split(/[A-Z]/).slice(1);
    const rightMiddle = rightMoves.indexOf("L");
    const leftPath = getPath4(`${edge}Left`);
    const leftMoves = leftPath.match(/[A-Z]/g) || [];
    const leftCoords = leftPath.split(/[A-Z]/).slice(1);
    const leftMiddle = leftMoves.indexOf("L");
    return {
      rightMoves,
      rightCoords,
      rightMiddle,
      leftMoves,
      leftCoords,
      leftMiddle
    };
  };
  const getTopPath = () => {
    const {
      topRight,
      topLeft
    } = cornerRadius;
    const arcLength = r2 * Math.abs(end - start);
    const {
      rightMoves,
      rightCoords,
      rightMiddle,
      leftMoves,
      leftCoords,
      leftMiddle
    } = getPathData("top");
    let moves2;
    let coords;
    if (topRight === topLeft || arcLength < 2 * topRight + 2 * topLeft) {
      moves2 = topRight > topLeft ? rightMoves : leftMoves;
      coords = topRight > topLeft ? rightCoords : leftCoords;
    } else {
      const isShort = (middle2) => middle2 < 3;
      const rightOffset = topLeft > topRight && isShort(rightMiddle) ? 1 : 2;
      let leftOffset;
      if (topRight > topLeft) {
        const defaultOffset = isShort(rightMiddle) ? leftMiddle : leftMiddle - 2;
        leftOffset = isShort(leftMiddle) ? leftMiddle - 1 : defaultOffset;
      } else {
        const defaultOffset = isShort(leftMiddle) ? 1 : 2;
        leftOffset = isShort(rightMiddle) ? defaultOffset : leftMiddle - 2;
      }
      moves2 = [...rightMoves.slice(0, rightOffset), ...leftMoves.slice(leftOffset)];
      coords = [...rightCoords.slice(0, rightOffset), ...leftCoords.slice(leftOffset)];
    }
    const middle = moves2.indexOf("L");
    const subMoves = moves2.slice(0, middle);
    const subCoords = coords.slice(0, middle);
    return subMoves.map((m, i) => ({
      command: m,
      coords: subCoords[i].split(",")
    }));
  };
  const getBottomPath = () => {
    const {
      bottomRight,
      bottomLeft
    } = cornerRadius;
    const arcLength = r1 * Math.abs(end - start);
    const {
      rightMoves,
      rightCoords,
      rightMiddle,
      leftMoves,
      leftCoords,
      leftMiddle
    } = getPathData("bottom");
    let moves2;
    let coords;
    if (bottomRight === bottomLeft || arcLength < 2 * bottomRight + 2 * bottomLeft) {
      moves2 = bottomRight > bottomLeft ? rightMoves : leftMoves;
      coords = bottomRight > bottomLeft ? rightCoords : leftCoords;
    } else {
      const isShort = (m, middle2) => m.length - middle2 < 4;
      const shortPath = bottomRight > bottomLeft ? isShort(rightMoves, rightMiddle) : isShort(leftMoves, leftMiddle);
      const rightOffset = shortPath ? -1 : -3;
      moves2 = [...leftMoves.slice(0, leftMiddle + 2), ...rightMoves.slice(rightOffset)];
      coords = [...leftCoords.slice(0, leftMiddle + 2), ...rightCoords.slice(rightOffset)];
    }
    const middle = moves2.indexOf("L");
    const subMoves = moves2.slice(middle, -1);
    const subCoords = coords.slice(middle, -1);
    return subMoves.map((m, i) => ({
      command: m,
      coords: subCoords[i].split(",")
    }));
  };
  const topPath = getTopPath();
  const bottomPath = getBottomPath();
  const moves = [...topPath, ...bottomPath];
  const path = moves.reduce((memo, move) => `${memo}${move.command} ${move.coords.join()}`, "");
  return `${path} z`;
};
var getBarPath = (props, width, cornerRadius) => {
  if (props.getPath) {
    return getCustomBarPath(props, width);
  }
  return props.horizontal ? getHorizontalBarPath(props, width, cornerRadius) : getVerticalBarPath(props, width, cornerRadius);
};
var getPolarBarPath = (props, cornerRadius) => {
  return getVerticalPolarBarPath(props, cornerRadius);
};

// node_modules/victory-bar/es/bar.js
var evaluateProps9 = (props) => {
  const style = getStyle2(props.style, props);
  const barWidth = getBarWidth(props.barWidth, Object.assign({}, props, {
    style
  }));
  const cornerRadius = getCornerRadius(props.cornerRadius, Object.assign({}, props, {
    style,
    barWidth
  }));
  const ariaLabel = helpers_exports.evaluateProp(props.ariaLabel, props);
  const desc = helpers_exports.evaluateProp(props.desc, props);
  const id = helpers_exports.evaluateProp(props.id, props);
  const tabIndex = helpers_exports.evaluateProp(props.tabIndex, props);
  return Object.assign({}, props, {
    ariaLabel,
    style,
    barWidth,
    cornerRadius,
    desc,
    id,
    tabIndex
  });
};
var defaultProps11 = {
  pathComponent: import_react37.default.createElement(Path, null),
  role: "presentation",
  shapeRendering: "auto"
};
var Bar = (0, import_react37.forwardRef)(function Bar2(initialProps, ref) {
  const props = evaluateProps9((0, import_defaults21.default)({}, initialProps, defaultProps11));
  const {
    polar,
    origin,
    style,
    barWidth,
    cornerRadius
  } = props;
  const path = polar ? getPolarBarPath(props, cornerRadius) : getBarPath(props, barWidth, cornerRadius);
  const defaultTransform = polar && origin ? `translate(${origin.x}, ${origin.y})` : void 0;
  if (!props.pathComponent) {
    return null;
  }
  return import_react37.default.cloneElement(props.pathComponent, {
    ...props.events,
    "aria-label": props.ariaLabel,
    style,
    d: path,
    className: props.className,
    clipPath: props.clipPath,
    desc: props.desc,
    index: props.index,
    role: props.role,
    shapeRendering: props.shapeRendering,
    transform: props.transform || defaultTransform,
    tabIndex: props.tabIndex,
    ref
  });
});

// node_modules/victory-bar/es/victory-bar.js
var fallbackProps3 = {
  width: 450,
  height: 300,
  padding: 50
};
var defaultData = [{
  x: 1,
  y: 1
}, {
  x: 2,
  y: 2
}, {
  x: 3,
  y: 3
}, {
  x: 4,
  y: 4
}];
var VictoryBarBase = class extends import_react38.default.Component {
  static getBaseProps(props) {
    return getBaseProps3(props, fallbackProps3);
  }
  // Overridden in native versions
  shouldAnimate() {
    return !!this.props.animate;
  }
  render() {
    const {
      animationWhitelist,
      role
    } = VictoryBar;
    const props = helpers_exports.modifyProps(this.props, fallbackProps3, role);
    if (this.shouldAnimate()) {
      return this.animateComponent(props, animationWhitelist);
    }
    const children = this.renderData(props);
    const component = props.standalone ? this.renderContainer(props.containerComponent, children) : children;
    return user_props_exports.withSafeUserProps(component, props);
  }
};
__publicField(VictoryBarBase, "animationWhitelist", ["data", "domain", "height", "padding", "style", "width"]);
__publicField(VictoryBarBase, "displayName", "VictoryBar");
__publicField(VictoryBarBase, "role", "bar");
__publicField(VictoryBarBase, "defaultTransitions", {
  onLoad: {
    duration: 2e3,
    before: () => ({
      _y: 0,
      _y1: 0,
      _y0: 0
    }),
    after: (datum) => ({
      _y: datum._y,
      _y1: datum._y1,
      _y0: datum._y0
    })
  },
  onExit: {
    duration: 500,
    before: () => ({
      _y: 0,
      yOffset: 0
    })
  },
  onEnter: {
    duration: 500,
    before: () => ({
      _y: 0,
      _y1: 0,
      _y0: 0
    }),
    after: (datum) => ({
      _y: datum._y,
      _y1: datum._y1,
      _y0: datum._y0
    })
  }
});
__publicField(VictoryBarBase, "defaultProps", {
  containerComponent: import_react38.default.createElement(VictoryContainer, null),
  data: defaultData,
  dataComponent: import_react38.default.createElement(Bar, null),
  groupComponent: import_react38.default.createElement("g", {
    role: "presentation"
  }),
  labelComponent: import_react38.default.createElement(VictoryLabel, null),
  samples: 50,
  sortOrder: "ascending",
  standalone: true,
  theme: VictoryTheme.grayscale
});
__publicField(VictoryBarBase, "getDomain", domain_exports.getDomainWithZero);
__publicField(VictoryBarBase, "getData", data_exports.getData);
__publicField(VictoryBarBase, "expectedComponents", ["dataComponent", "labelComponent", "groupComponent", "containerComponent"]);
var VictoryBar = addEvents(VictoryBarBase);

// node_modules/victory-box-plot/es/victory-box-plot.js
var import_react39 = __toESM(require_react());

// node_modules/victory-box-plot/es/helper-methods.js
var import_groupBy2 = __toESM(require_groupBy());
var import_uniq5 = __toESM(require_uniq());
var import_defaults22 = __toESM(require_defaults());
var import_orderBy4 = __toESM(require_orderBy());
var TYPES = ["max", "min", "median", "q1", "q3"];
var checkProcessedData = (data) => {
  const hasQuartileAttributes = data.every((datum) => {
    return TYPES.every((val) => typeof datum[`_${val}`] !== "undefined");
  });
  if (hasQuartileAttributes) {
    const values = data.map((d) => d._x);
    if (!(0, import_uniq5.default)(values).length === values.length) {
      throw new Error(`
        data prop may only take an array of objects with a unique
        independent variable. Make sure your x values are distinct.
      `);
    }
    return true;
  }
  return false;
};
var nanToNull = (val) => Number.isNaN(val) ? null : val;
var getSummaryStatistics = (data) => {
  const dependentVars = data.map((datum) => datum._y);
  const quartiles = {
    _q1: nanToNull(quantile(dependentVars, 0.25)),
    // eslint-disable-line no-magic-numbers
    _q3: nanToNull(quantile(dependentVars, 0.75)),
    // eslint-disable-line no-magic-numbers
    _min: nanToNull(min(dependentVars)),
    _median: nanToNull(quantile(dependentVars, 0.5)),
    _max: nanToNull(max(dependentVars))
  };
  return Object.assign({}, data[0], quartiles, {
    _y: data[0]._y
  });
};
var processData = (data) => {
  const isProcessed = checkProcessedData(data);
  if (!isProcessed) {
    const arrayX = data.every((datum) => Array.isArray(datum._x));
    const arrayY = data.every((datum) => Array.isArray(datum._y));
    const sortKey = "_y";
    const groupKey = "_x";
    if (arrayX) {
      throw new Error(`
        data should not be given as in array for x
      `);
    } else if (arrayY) {
      return data.map((datum) => {
        const dataArray = datum[sortKey].map((d) => Object.assign({}, datum, {
          [sortKey]: d
        }));
        const sortedData = (0, import_orderBy4.default)(dataArray, sortKey);
        return getSummaryStatistics(sortedData);
      });
    } else {
      const groupedData = (0, import_groupBy2.default)(data, groupKey);
      return Object.keys(groupedData).map((key) => {
        const datum = groupedData[key];
        const sortedData = (0, import_orderBy4.default)(datum, sortKey);
        return getSummaryStatistics(sortedData);
      });
    }
  } else {
    return data;
  }
};
var getData3 = (props) => {
  const accessorTypes = TYPES.concat("x", "y");
  const formattedData = data_exports.formatData(props.data, props, accessorTypes);
  return formattedData.length ? processData(formattedData) : [];
};
var reduceDataset = (dataset, props, axis) => {
  const minDomain = domain_exports.getMinFromProps(props, axis);
  const maxDomain = domain_exports.getMaxFromProps(props, axis);
  const minData = minDomain !== void 0 ? minDomain : dataset.reduce((memo, datum) => {
    return memo < datum[`_${axis}`] ? memo : datum[`_${axis}`];
  }, Infinity);
  const maxData = maxDomain !== void 0 ? maxDomain : dataset.reduce((memo, datum) => {
    return memo > datum[`_${axis}`] ? memo : datum[`_${axis}`];
  }, -Infinity);
  return domain_exports.getDomainFromMinMax(minData, maxData);
};
var getDomainFromMinMaxValues = (dataset, props, axis) => {
  const minDomain = domain_exports.getMinFromProps(props, axis);
  const maxDomain = domain_exports.getMaxFromProps(props, axis);
  const minData = minDomain !== void 0 ? minDomain : dataset.reduce((memo, datum) => {
    return memo < datum._min ? memo : datum._min;
  }, Infinity);
  const maxData = maxDomain !== void 0 ? maxDomain : dataset.reduce((memo, datum) => {
    return memo > datum._max ? memo : datum._max;
  }, -Infinity);
  return domain_exports.getDomainFromMinMax(minData, maxData);
};
var getDomainFromData3 = (props, axis) => {
  const minDomain = domain_exports.getMinFromProps(props, axis);
  const maxDomain = domain_exports.getMaxFromProps(props, axis);
  const dataset = getData3(props);
  if (dataset.length < 1) {
    return minDomain !== void 0 && maxDomain !== void 0 ? domain_exports.getDomainFromMinMax(minDomain, maxDomain) : void 0;
  }
  return axis === "y" ? getDomainFromMinMaxValues(dataset, props, axis) : reduceDataset(dataset, props, axis);
};
var getDomain4 = (props, axis) => {
  return domain_exports.createDomainFunction(getDomainFromData3)(props, axis);
};
var getLabelStyle = (props, styleObject, namespace) => {
  const component = props[`${namespace}LabelComponent`] || props.labelComponent;
  const baseStyle = styleObject[`${namespace}Labels`] || styleObject.labels;
  if (!helpers_exports.isTooltip(component)) {
    return baseStyle;
  }
  const tooltipTheme = props.theme && props.theme.tooltip || {};
  return (0, import_defaults22.default)({}, tooltipTheme.style, baseStyle);
};
var getStyles4 = function(props, styleObject) {
  if (styleObject === void 0) {
    styleObject = {};
  }
  if (props.disableInlineStyles) {
    return {};
  }
  const style = props.style || {};
  const parentStyles = {
    height: "100%",
    width: "100%"
  };
  const labelStyles = (0, import_defaults22.default)({}, style.labels, getLabelStyle(props, styleObject));
  const boxStyles = (0, import_defaults22.default)({}, style.boxes, styleObject.boxes);
  const whiskerStyles = (0, import_defaults22.default)({}, style.whiskers, styleObject.whiskers);
  return {
    boxes: boxStyles,
    labels: labelStyles,
    parent: (0, import_defaults22.default)({}, style.parent, styleObject.parent, parentStyles),
    max: (0, import_defaults22.default)({}, style.max, styleObject.max, whiskerStyles),
    maxLabels: (0, import_defaults22.default)({}, style.maxLabels, getLabelStyle(props, styleObject, "max"), labelStyles),
    median: (0, import_defaults22.default)({}, style.median, styleObject.median, whiskerStyles),
    medianLabels: (0, import_defaults22.default)({}, style.medianLabels, getLabelStyle(props, styleObject, "median"), labelStyles),
    min: (0, import_defaults22.default)({}, style.min, styleObject.min, whiskerStyles),
    minLabels: (0, import_defaults22.default)({}, style.minLabels, getLabelStyle(props, styleObject, "min"), labelStyles),
    q1: (0, import_defaults22.default)({}, style.q1, styleObject.q1, boxStyles),
    q1Labels: (0, import_defaults22.default)({}, style.q1Labels, getLabelStyle(props, styleObject, "q1"), labelStyles),
    q3: (0, import_defaults22.default)({}, style.q3, styleObject.q3, boxStyles),
    q3Labels: (0, import_defaults22.default)({}, style.q3Labels, getLabelStyle(props, styleObject, "q3"), labelStyles),
    whiskers: whiskerStyles
  };
};
var getCalculatedValues4 = (props) => {
  const {
    theme,
    horizontal
  } = props;
  const data = getData3(props);
  const range3 = {
    x: helpers_exports.getRange(props, "x"),
    y: helpers_exports.getRange(props, "y")
  };
  const domain = {
    x: getDomain4(props, "x"),
    y: getDomain4(props, "y")
  };
  const scale = {
    x: scale_exports.getBaseScale(props, "x").domain(domain.x).range(props.horizontal ? range3.y : range3.x),
    y: scale_exports.getBaseScale(props, "y").domain(domain.y).range(props.horizontal ? range3.x : range3.y)
  };
  const defaultStyles2 = theme && theme.boxplot && theme.boxplot.style ? theme.boxplot.style : {};
  const style = getStyles4(props, defaultStyles2);
  const defaultOrientation = props.horizontal ? "top" : "right";
  const labelOrientation = props.labelOrientation || defaultOrientation;
  const boxWidth = props.boxWidth || 1;
  return {
    data,
    horizontal,
    domain,
    scale,
    style,
    labelOrientation,
    boxWidth
  };
};
var getWhiskerProps = (props, type) => {
  const {
    horizontal,
    style,
    boxWidth,
    whiskerWidth,
    datum,
    scale,
    index,
    disableInlineStyles
  } = props;
  const {
    min: min2,
    max: max2,
    q1,
    q3,
    x: x2,
    y: y2
  } = props.positions;
  const boxValue = type === "min" ? q1 : q3;
  const whiskerValue = type === "min" ? min2 : max2;
  const width = typeof whiskerWidth === "number" ? whiskerWidth : boxWidth;
  return {
    datum,
    index,
    scale,
    majorWhisker: {
      x1: horizontal ? boxValue : x2,
      y1: horizontal ? y2 : boxValue,
      x2: horizontal ? whiskerValue : x2,
      y2: horizontal ? y2 : whiskerValue
    },
    minorWhisker: {
      x1: horizontal ? whiskerValue : x2 - width / 2,
      y1: horizontal ? y2 - width / 2 : whiskerValue,
      x2: horizontal ? whiskerValue : x2 + width / 2,
      y2: horizontal ? y2 + width / 2 : whiskerValue
    },
    style: disableInlineStyles ? {} : style[type] || style.whisker,
    disableInlineStyles
  };
};
var getBoxProps = (props, type) => {
  const {
    horizontal,
    boxWidth,
    style,
    scale,
    datum,
    index,
    disableInlineStyles
  } = props;
  const {
    median,
    q1,
    q3,
    x: x2,
    y: y2
  } = props.positions;
  const defaultX = type === "q1" ? q1 : median;
  const defaultY = type === "q1" ? median : q3;
  const defaultWidth = type === "q1" ? median - q1 : q3 - median;
  const defaultHeight = type === "q1" ? q1 - median : median - q3;
  return {
    datum,
    scale,
    index,
    x: horizontal ? defaultX : x2 - boxWidth / 2,
    y: horizontal ? y2 - boxWidth / 2 : defaultY,
    width: horizontal ? defaultWidth : boxWidth,
    height: horizontal ? boxWidth : defaultHeight,
    style: disableInlineStyles ? {} : style[type] || style.boxes,
    disableInlineStyles
  };
};
var getMedianProps = (props) => {
  const {
    boxWidth,
    horizontal,
    style,
    datum,
    scale,
    index,
    disableInlineStyles
  } = props;
  const {
    median,
    x: x2,
    y: y2
  } = props.positions;
  return {
    datum,
    scale,
    index,
    x1: horizontal ? median : x2 - boxWidth / 2,
    y1: horizontal ? y2 - boxWidth / 2 : median,
    x2: horizontal ? median : x2 + boxWidth / 2,
    y2: horizontal ? y2 + boxWidth / 2 : median,
    style: disableInlineStyles ? {} : style.median,
    disableInlineStyles
  };
};
var getText2 = (props, type) => {
  const {
    datum,
    index,
    labels
  } = props;
  const propName = `${type}Labels`;
  const labelProp = props[propName];
  if (!labelProp && !labels) {
    return null;
  } else if (labelProp === true || labels === true) {
    const dataName = `_${type}`;
    return `${datum[dataName]}`;
  }
  return Array.isArray(labelProp) ? labelProp[index] : labelProp;
};
var getOrientation2 = (labelOrientation, type) => typeof labelOrientation === "object" && labelOrientation[type] || labelOrientation;
var getLabelProps = (props, text, type) => {
  const {
    datum,
    positions,
    index,
    boxWidth,
    horizontal,
    labelOrientation,
    style,
    theme,
    disableInlineStyles
  } = props;
  const orientation = getOrientation2(labelOrientation, type);
  const namespace = `${type}Labels`;
  const labelStyle = style[namespace] || style.labels;
  const defaultVerticalAnchors = {
    top: "end",
    bottom: "start",
    left: "middle",
    right: "middle"
  };
  const defaultTextAnchors = {
    left: "end",
    right: "start",
    top: "middle",
    bottom: "middle"
  };
  const whiskerWidth = typeof props.whiskerWidth === "number" ? props.whiskerWidth : boxWidth;
  const width = type === "min" || type === "max" ? whiskerWidth : boxWidth;
  const getOffset4 = (coord) => {
    const sign = {
      x: orientation === "left" ? -1 : 1,
      y: orientation === "top" ? -1 : 1
    };
    return sign[coord] * width / 2 + sign[coord] * (labelStyle.padding || 0);
  };
  const labelProps = {
    text,
    datum,
    index,
    orientation,
    style: disableInlineStyles ? {} : labelStyle,
    y: horizontal ? positions.y : positions[type],
    x: horizontal ? positions[type] : positions.x,
    dy: horizontal ? getOffset4("y") : 0,
    dx: horizontal ? 0 : getOffset4("x"),
    textAnchor: labelStyle.textAnchor || defaultTextAnchors[orientation],
    verticalAnchor: labelStyle.verticalAnchor || defaultVerticalAnchors[orientation],
    angle: labelStyle.angle,
    horizontal,
    disableInlineStyles
  };
  const component = props[`${type}LabelComponent`];
  if (!helpers_exports.isTooltip(component)) {
    return labelProps;
  }
  const tooltipTheme = theme && theme.tooltip || {};
  return (0, import_defaults22.default)({}, labelProps, helpers_exports.omit(tooltipTheme, ["style"]));
};
var getDataProps = (props, type) => {
  if (type === "median") {
    return getMedianProps(props);
  } else if (type === "min" || type === "max") {
    return getWhiskerProps(props, type);
  }
  return getBoxProps(props, type);
};
var isDatumOutOfBounds = (datum, domain) => {
  const exists2 = (val) => val !== void 0;
  const {
    _x,
    _min,
    _max
  } = datum;
  const minDomainX = collection_exports.getMinValue(domain.x);
  const maxDomainX = collection_exports.getMaxValue(domain.x);
  const minDomainY = collection_exports.getMinValue(domain.y);
  const maxDomainY = collection_exports.getMaxValue(domain.y);
  const underMin = (min2) => (val) => exists2(val) && val < min2;
  const overMax = (max2) => (val) => exists2(val) && val > max2;
  const isUnderMinX = underMin(minDomainX);
  const isUnderMinY = underMin(minDomainY);
  const isOverMaxX = overMax(maxDomainX);
  const isOverMaxY = overMax(maxDomainY);
  let yOutOfBounds;
  let xOutOfBounds;
  if (isUnderMinX(_x) || isOverMaxX(_x)) xOutOfBounds = true;
  if (isUnderMinY(_min) && isUnderMinY(_max) || isOverMaxY(_min) && isOverMaxY(_max)) yOutOfBounds = true;
  return yOutOfBounds || xOutOfBounds;
};
var getBaseProps4 = (initialProps, fallbackProps22) => {
  const modifiedProps = helpers_exports.modifyProps(initialProps, fallbackProps22, "boxplot");
  const props = Object.assign({}, modifiedProps, getCalculatedValues4(modifiedProps));
  const {
    groupComponent,
    width,
    height,
    padding: padding2,
    standalone,
    theme,
    events,
    sharedEvents,
    scale,
    horizontal,
    data,
    style,
    domain,
    name
  } = props;
  const initialChildProps = {
    parent: {
      domain,
      scale,
      width,
      height,
      data,
      standalone,
      name,
      theme,
      style: style.parent || {},
      padding: padding2,
      groupComponent,
      horizontal
    }
  };
  const boxScale = scale.y;
  return data.reduce((acc, datum, index) => {
    const eventKey = !helpers_exports.isNil(datum.eventKey) ? datum.eventKey : index;
    if (isDatumOutOfBounds(datum, domain)) return acc;
    const positions = {
      x: horizontal ? scale.y(datum._y) : scale.x(datum._x),
      y: horizontal ? scale.x(datum._x) : scale.y(datum._y),
      min: boxScale(datum._min),
      max: boxScale(datum._max),
      median: boxScale(datum._median),
      q1: boxScale(datum._q1),
      q3: boxScale(datum._q3)
    };
    const dataProps = Object.assign({
      index,
      datum,
      positions
    }, props);
    const dataObj = TYPES.reduce((memo, type) => {
      memo[type] = getDataProps(dataProps, type);
      return memo;
    }, {});
    acc[eventKey] = dataObj;
    TYPES.forEach((type) => {
      const labelText = getText2(dataProps, type);
      const labelProp = props.labels || props[`${type}Labels`];
      if (labelText !== null && labelText !== void 0 || labelProp && (events || sharedEvents)) {
        const target = `${type}Labels`;
        acc[eventKey][target] = getLabelProps(Object.assign({}, props, dataProps), labelText, type);
      }
    });
    return acc;
  }, initialChildProps);
};

// node_modules/victory-box-plot/es/victory-box-plot.js
var fallbackProps4 = {
  width: 450,
  height: 300,
  padding: {
    top: 20,
    right: 20,
    bottom: 20,
    left: 20
  }
};
var defaultData2 = [{
  x: 1,
  min: 5,
  q1: 7,
  median: 12,
  q3: 18,
  max: 20
}, {
  x: 2,
  min: 2,
  q1: 5,
  median: 8,
  q3: 12,
  max: 15
}];
var options3 = {
  components: [{
    name: "min"
  }, {
    name: "minLabels"
  }, {
    name: "max"
  }, {
    name: "maxLabels"
  }, {
    name: "median"
  }, {
    name: "medianLabels"
  }, {
    name: "q1"
  }, {
    name: "q1Labels"
  }, {
    name: "q3"
  }, {
    name: "q3Labels"
  }, {
    name: "parent",
    index: "parent"
  }]
};
var VictoryBoxPlotBase = class extends import_react39.default.Component {
  static getDomain(props, axis) {
    return getDomain4(props, axis);
  }
  static getData(props) {
    return getData3(props);
  }
  static getBaseProps(props) {
    return getBaseProps4(props, fallbackProps4);
  }
  renderBoxPlot(props) {
    const types = ["q1", "q3", "max", "min", "median"];
    const dataComponents = types.map((type) => {
      return this.dataKeys.reduce((validDataComponents, _key, index) => {
        const baseComponent = props[`${type}Component`];
        const componentProps = this.getComponentProps(baseComponent, type, index);
        if (this.shouldRenderDatum(componentProps.datum)) {
          validDataComponents.push(import_react39.default.cloneElement(baseComponent, componentProps));
        }
        return validDataComponents;
      }, []);
    }).flat();
    const labelComponents = types.map((type) => {
      const components = this.dataKeys.reduce((validComponents, _key, index) => {
        const name = `${type}Labels`;
        const baseComponent = props[`${type}LabelComponent`];
        const labelProps = this.getComponentProps(baseComponent, name, index);
        if (labelProps.text !== void 0 && labelProps.text !== null) {
          validComponents.push(import_react39.default.cloneElement(baseComponent, labelProps));
        }
        return validComponents;
      }, []);
      return components.filter(Boolean);
    }).flat();
    const children = [...dataComponents, ...labelComponents];
    return this.renderContainer(props.groupComponent, children);
  }
  // Overridden in native versions
  shouldAnimate() {
    return !!this.props.animate;
  }
  shouldRenderDatum(datum) {
    const hasX = !helpers_exports.isNil(datum._x);
    const hasY = !helpers_exports.isNil(datum._y);
    const hasSummaryStatistics = !helpers_exports.isNil(datum._min) && !helpers_exports.isNil(datum._max) && !helpers_exports.isNil(datum._median) && !helpers_exports.isNil(datum._q1) && !helpers_exports.isNil(datum._q3);
    return hasSummaryStatistics && (this.props.horizontal ? hasY : hasX);
  }
  render() {
    const {
      animationWhitelist,
      role
    } = VictoryBoxPlot;
    const props = helpers_exports.modifyProps(this.props, fallbackProps4, role);
    if (this.shouldAnimate()) {
      return this.animateComponent(props, animationWhitelist);
    }
    const children = this.renderBoxPlot(props);
    const component = props.standalone ? this.renderContainer(props.containerComponent, children) : children;
    return user_props_exports.withSafeUserProps(component, props);
  }
};
__publicField(VictoryBoxPlotBase, "animationWhitelist", ["data", "domain", "height", "padding", "style", "width"]);
__publicField(VictoryBoxPlotBase, "displayName", "VictoryBoxPlot");
__publicField(VictoryBoxPlotBase, "role", "boxplot");
__publicField(VictoryBoxPlotBase, "defaultTransitions", default_transitions_exports.discreteTransitions());
__publicField(VictoryBoxPlotBase, "defaultProps", {
  containerComponent: import_react39.default.createElement(VictoryContainer, null),
  data: defaultData2,
  dataComponent: import_react39.default.createElement(Border, null),
  groupComponent: import_react39.default.createElement("g", {
    role: "presentation"
  }),
  maxComponent: import_react39.default.createElement(Whisker, null),
  maxLabelComponent: import_react39.default.createElement(VictoryLabel, null),
  medianComponent: import_react39.default.createElement(LineSegment, null),
  medianLabelComponent: import_react39.default.createElement(VictoryLabel, null),
  minComponent: import_react39.default.createElement(Whisker, null),
  minLabelComponent: import_react39.default.createElement(VictoryLabel, null),
  q1Component: import_react39.default.createElement(Border, null),
  q1LabelComponent: import_react39.default.createElement(VictoryLabel, null),
  q3Component: import_react39.default.createElement(Border, null),
  q3LabelComponent: import_react39.default.createElement(VictoryLabel, null),
  samples: 50,
  sortKey: "x",
  sortOrder: "ascending",
  standalone: true,
  theme: VictoryTheme.grayscale
});
__publicField(VictoryBoxPlotBase, "expectedComponents", ["maxComponent", "maxLabelComponent", "medianComponent", "medianLabelComponent", "minComponent", "minLabelComponent", "q1Component", "q1LabelComponent", "q3Component", "q3LabelComponent", "groupComponent", "containerComponent"]);
var VictoryBoxPlot = addEvents(VictoryBoxPlotBase, options3);

// node_modules/victory-brush-container/es/victory-brush-container.js
var import_defaults24 = __toESM(require_defaults());
var import_react40 = __toESM(require_react());

// node_modules/victory-brush-container/es/brush-helpers.js
var import_defaults23 = __toESM(require_defaults());
var import_throttle = __toESM(require_throttle());
var import_react_fast_compare3 = __toESM(require_react_fast_compare());
var Helpers = {
  getDimension(props) {
    const {
      horizontal,
      brushDimension
    } = props;
    if (!horizontal || !brushDimension) {
      return brushDimension;
    }
    return brushDimension === "x" ? "y" : "x";
  },
  withinBounds(point3, bounds, padding2) {
    const {
      x1,
      x2,
      y1,
      y2
    } = helpers_exports.mapValues(bounds, Number);
    const {
      x: x3,
      y: y3
    } = helpers_exports.mapValues(point3, Number);
    const paddingValue = padding2 ? padding2 / 2 : 0;
    return x3 + paddingValue >= Math.min(x1, x2) && x3 - paddingValue <= Math.max(x1, x2) && y3 + paddingValue >= Math.min(y1, y2) && y3 - paddingValue <= Math.max(y1, y2);
  },
  getDomainBox(props, fullDomain, selectedDomain) {
    const brushDimension = this.getDimension(props);
    const fullDomainObject = (0, import_defaults23.default)({}, fullDomain, props.domain);
    const selectedDomainObject = (0, import_defaults23.default)({}, selectedDomain, fullDomainObject);
    const fullCoords = selection_exports.getDomainCoordinates(props, fullDomainObject);
    const selectedCoords = selection_exports.getDomainCoordinates(props, selectedDomainObject);
    return {
      x1: brushDimension !== "y" ? Math.min(...selectedCoords.x) : Math.min(...fullCoords.x),
      x2: brushDimension !== "y" ? Math.max(...selectedCoords.x) : Math.max(...fullCoords.x),
      y1: brushDimension !== "x" ? Math.min(...selectedCoords.y) : Math.min(...fullCoords.y),
      y2: brushDimension !== "x" ? Math.max(...selectedCoords.y) : Math.max(...fullCoords.y)
    };
  },
  getHandles(props, domainBox) {
    const brushDimension = this.getDimension(props);
    const {
      x1,
      x2,
      y1,
      y2
    } = domainBox;
    const minX = Math.min(x1, x2);
    const maxX = Math.max(x1, x2);
    const minY = Math.min(y1, y2);
    const maxY = Math.max(y1, y2);
    const handleWidth = props.handleWidth / 2;
    return {
      left: brushDimension !== "y" && {
        x1: minX - handleWidth,
        x2: minX + handleWidth,
        y1,
        y2
      },
      right: brushDimension !== "y" && {
        x1: maxX - handleWidth,
        x2: maxX + handleWidth,
        y1,
        y2
      },
      top: brushDimension !== "x" && {
        x1,
        x2,
        y1: minY - handleWidth,
        y2: minY + handleWidth
      },
      bottom: brushDimension !== "x" && {
        x1,
        x2,
        y1: maxY - handleWidth,
        y2: maxY + handleWidth
      }
    };
  },
  getActiveHandles(point3, props, domainBox) {
    const handles = this.getHandles(props, domainBox);
    const activeHandles = ["top", "bottom", "left", "right"].reduce((memo, opt) => handles[opt] && this.withinBounds(point3, handles[opt]) ? memo.concat(opt) : memo, []);
    return activeHandles.length && activeHandles;
  },
  getResizeMutation(box, handles) {
    const {
      x1,
      y1,
      x2,
      y2
    } = box;
    const mutations = {
      left: {
        x1: Math.max(x1, x2),
        x2: Math.min(x1, x2),
        y1,
        y2
      },
      right: {
        x1: Math.min(x1, x2),
        x2: Math.max(x1, x2),
        y1,
        y2
      },
      top: {
        y1: Math.max(y1, y2),
        y2: Math.min(y1, y2),
        x1,
        x2
      },
      bottom: {
        y1: Math.min(y1, y2),
        y2: Math.max(y1, y2),
        x1,
        x2
      }
    };
    return handles.reduce((memo, current) => {
      return Object.assign(memo, mutations[current]);
    }, {});
  },
  getMinimumDomain() {
    return {
      x: [0, 1 / Number.MAX_SAFE_INTEGER],
      y: [0, 1 / Number.MAX_SAFE_INTEGER]
    };
  },
  getDefaultBrushArea(targetProps, cachedDomain, evt) {
    const {
      domain,
      fullDomain,
      scale,
      horizontal,
      allowResize
    } = targetProps;
    const defaultBrushArea = !allowResize && !targetProps.defaultBrushArea ? "move" : targetProps.defaultBrushArea;
    if (defaultBrushArea === "none") {
      return this.getMinimumDomain();
    } else if (defaultBrushArea === "disable") {
      return cachedDomain;
    } else if (defaultBrushArea === "move") {
      const brushBox = this.getDomainBox(targetProps, fullDomain, cachedDomain);
      const parentSVG = targetProps.parentSVG || selection_exports.getParentSVG(evt);
      const pannedBox = this.panBox({
        ...targetProps,
        ...brushBox,
        brushDomain: cachedDomain,
        startX: (brushBox.x1 + brushBox.x2) / 2,
        startY: (brushBox.y1 + brushBox.y2) / 2
      }, selection_exports.getSVGEventCoordinates(evt, parentSVG));
      const fullDomainBox = targetProps.fullDomainBox || this.getDomainBox(targetProps, fullDomain);
      const constrainedBox = this.constrainBox(pannedBox, fullDomainBox);
      return selection_exports.getBounds({
        ...constrainedBox,
        scale,
        horizontal
      });
    }
    return domain;
  },
  getSelectionMutation(point3, box, brushDimension) {
    const {
      x: x2,
      y: y2
    } = point3;
    const {
      x1,
      x2: x22,
      y1,
      y2: y22
    } = box;
    return {
      x1: brushDimension !== "y" ? x2 : x1,
      y1: brushDimension !== "x" ? y2 : y1,
      x2: brushDimension !== "y" ? x2 : x22,
      y2: brushDimension !== "x" ? y2 : y22
    };
  },
  panBox(props, point3) {
    const {
      domain,
      startX,
      startY
    } = props;
    const brushDimension = this.getDimension(props);
    const brushDomain = (0, import_defaults23.default)({}, props.brushDomain, domain);
    const fullDomain = (0, import_defaults23.default)({}, props.fullDomain, domain);
    const {
      x1,
      x2,
      y1,
      y2
    } = props.x1 ? props : this.getDomainBox(props, fullDomain, brushDomain);
    const {
      x: x3,
      y: y3
    } = point3;
    const delta = {
      x: startX ? startX - x3 : 0,
      y: startY ? startY - y3 : 0
    };
    return {
      x1: brushDimension !== "y" ? Math.min(x1, x2) - delta.x : Math.min(x1, x2),
      x2: brushDimension !== "y" ? Math.max(x1, x2) - delta.x : Math.max(x1, x2),
      y1: brushDimension !== "x" ? Math.min(y1, y2) - delta.y : Math.min(y1, y2),
      y2: brushDimension !== "x" ? Math.max(y1, y2) - delta.y : Math.max(y1, y2)
    };
  },
  constrainBox(box, fullDomainBox) {
    const {
      x1,
      y1,
      x2,
      y2
    } = helpers_exports.mapValues(fullDomainBox, Number);
    return {
      x1: box.x2 > x2 ? x2 - Math.abs(box.x2 - box.x1) : Math.max(box.x1, x1),
      y1: box.y2 > y2 ? y2 - Math.abs(box.y2 - box.y1) : Math.max(box.y1, y1),
      x2: box.x1 < x1 ? x1 + Math.abs(box.x2 - box.x1) : Math.min(box.x2, x2),
      y2: box.y1 < y1 ? y1 + Math.abs(box.y2 - box.y1) : Math.min(box.y2, y2)
    };
  },
  constrainPoint(point3, fullDomainBox) {
    const {
      x1,
      y1,
      x2,
      y2
    } = helpers_exports.mapValues(fullDomainBox, Number);
    return {
      x: Math.min(Math.max(point3.x, x1), x2),
      y: Math.min(Math.max(point3.y, y1), y2)
    };
  },
  hasMoved(props) {
    const {
      x1,
      x2,
      y1,
      y2,
      mouseMoveThreshold
    } = props;
    const brushDimension = this.getDimension(props);
    const xMoved = Math.abs(x1 - x2) >= mouseMoveThreshold;
    const yMoved = Math.abs(y1 - y2) >= mouseMoveThreshold;
    switch (brushDimension) {
      case "x":
        return xMoved;
      case "y":
        return yMoved;
      default:
        return xMoved || yMoved;
    }
  },
  // eslint-disable-next-line max-statements, complexity
  onMouseDown(evt, targetProps) {
    evt.preventDefault();
    const {
      handleWidth,
      cachedBrushDomain,
      domain,
      allowResize,
      allowDrag,
      allowDraw
    } = targetProps;
    const brushDimension = this.getDimension(targetProps);
    const defaultBrushArea = !allowResize && !targetProps.defaultBrushArea ? "move" : targetProps.defaultBrushArea;
    if (!allowResize && !allowDrag) {
      return {};
    }
    const fullDomainBox = targetProps.fullDomainBox || this.getDomainBox(targetProps, domain);
    const parentSVG = targetProps.parentSVG || selection_exports.getParentSVG(evt);
    const {
      x: x2,
      y: y2
    } = selection_exports.getSVGEventCoordinates(evt, parentSVG);
    if (!this.withinBounds({
      x: x2,
      y: y2
    }, fullDomainBox, handleWidth)) {
      return {};
    }
    const brushDomain = (0, import_defaults23.default)({}, targetProps.brushDomain, domain);
    const currentDomain = (0, import_react_fast_compare3.default)(brushDomain, cachedBrushDomain) ? targetProps.currentDomain || brushDomain || domain : brushDomain || domain;
    const domainBox = this.getDomainBox(targetProps, domain, currentDomain);
    const activeHandles = allowResize && this.getActiveHandles({
      x: x2,
      y: y2
    }, targetProps, domainBox);
    if (activeHandles) {
      return [{
        target: "parent",
        mutation: () => {
          return {
            isSelecting: true,
            domainBox,
            fullDomainBox,
            cachedBrushDomain: brushDomain,
            currentDomain,
            parentSVG,
            ...this.getResizeMutation(domainBox, activeHandles)
          };
        }
      }];
    } else if (this.withinBounds({
      x: x2,
      y: y2
    }, domainBox) && !(0, import_react_fast_compare3.default)(domain, currentDomain)) {
      return [{
        target: "parent",
        mutation: () => ({
          isPanning: allowDrag,
          startX: x2,
          startY: y2,
          domainBox,
          fullDomainBox,
          currentDomain,
          cachedBrushDomain: brushDomain,
          parentSVG,
          ...domainBox
          // set x1, x2, y1, y2
        })
      }];
    }
    return allowDraw ? [{
      target: "parent",
      mutation: () => ({
        isSelecting: allowResize || defaultBrushArea === "move",
        domainBox,
        fullDomainBox,
        parentSVG,
        cachedBrushDomain: brushDomain,
        cachedCurrentDomain: currentDomain,
        currentDomain: this.getMinimumDomain(),
        ...this.getSelectionMutation({
          x: x2,
          y: y2
        }, domainBox, brushDimension)
      })
    }] : {};
  },
  // eslint-disable-next-line max-statements, complexity
  onGlobalMouseMove(evt, targetProps) {
    const {
      scale,
      isPanning,
      isSelecting,
      fullDomainBox,
      onBrushDomainChange,
      allowResize,
      allowDrag,
      horizontal,
      mouseMoveThreshold,
      parentSVG
    } = targetProps;
    const brushDimension = this.getDimension(targetProps);
    const {
      x: x2,
      y: y2
    } = selection_exports.getSVGEventCoordinates(evt, parentSVG);
    if (!allowResize && !allowDrag || mouseMoveThreshold > 0 && !this.hasMoved({
      ...targetProps,
      x2,
      y2
    })) {
      return {};
    }
    if (allowDrag && isPanning) {
      const {
        startX,
        startY
      } = targetProps;
      const pannedBox = this.panBox(targetProps, {
        x: x2,
        y: y2
      });
      const constrainedBox = this.constrainBox(pannedBox, fullDomainBox);
      const currentDomain = selection_exports.getBounds({
        ...constrainedBox,
        scale,
        horizontal
      });
      const mutatedProps = {
        currentDomain,
        parentSVG,
        startX: pannedBox.x2 >= fullDomainBox.x2 || pannedBox.x1 <= fullDomainBox.x1 ? startX : x2,
        startY: pannedBox.y2 >= fullDomainBox.y2 || pannedBox.y1 <= fullDomainBox.y1 ? startY : y2,
        ...constrainedBox
      };
      if (helpers_exports.isFunction(onBrushDomainChange)) {
        onBrushDomainChange(currentDomain, (0, import_defaults23.default)({}, mutatedProps, targetProps));
      }
      return [{
        target: "parent",
        mutation: () => mutatedProps
      }];
    } else if (allowResize && isSelecting) {
      const {
        x: x22,
        y: y22
      } = this.constrainPoint({
        x: brushDimension !== "y" ? x2 : targetProps.x2,
        y: brushDimension !== "x" ? y2 : targetProps.y2
      }, fullDomainBox);
      const currentDomain = selection_exports.getBounds({
        x2: x22,
        y2: y22,
        x1: targetProps.x1,
        y1: targetProps.y1,
        scale,
        horizontal
      });
      const mutatedProps = {
        x2: x22,
        y2: y22,
        currentDomain,
        parentSVG
      };
      if (helpers_exports.isFunction(onBrushDomainChange)) {
        onBrushDomainChange(currentDomain, (0, import_defaults23.default)({}, mutatedProps, targetProps));
      }
      return [{
        target: "parent",
        mutation: () => mutatedProps
      }];
    }
    return {};
  },
  // eslint-disable-next-line complexity
  onGlobalMouseUp(evt, targetProps) {
    if (!targetProps.isPanning && !targetProps.isSelecting) {
      return {};
    }
    const {
      x1,
      y1,
      x2,
      y2,
      isPanning,
      isSelecting,
      onBrushDomainChange,
      onBrushDomainChangeEnd,
      onBrushCleared,
      currentDomain,
      allowResize,
      allowDrag
    } = targetProps;
    const defaultBrushArea = !allowResize && !targetProps.defaultBrushArea ? "move" : targetProps.defaultBrushArea;
    const defaultBrushHasArea = defaultBrushArea !== void 0 && defaultBrushArea !== "none";
    const mutatedProps = {
      isPanning: false,
      isSelecting: false
    };
    if ((allowResize || defaultBrushHasArea) && (x1 === x2 || y1 === y2)) {
      const cachedDomain = targetProps.cachedCurrentDomain || currentDomain;
      const defaultDomain = this.getDefaultBrushArea(targetProps, cachedDomain, evt);
      mutatedProps.currentDomain = defaultDomain;
      if (helpers_exports.isFunction(onBrushDomainChange)) {
        onBrushDomainChange(defaultDomain, (0, import_defaults23.default)({}, mutatedProps, targetProps));
      }
      if (helpers_exports.isFunction(onBrushDomainChangeEnd)) {
        onBrushDomainChangeEnd(defaultDomain, (0, import_defaults23.default)({}, mutatedProps, targetProps));
      }
      if (helpers_exports.isFunction(onBrushCleared)) {
        onBrushCleared(defaultDomain, (0, import_defaults23.default)({}, mutatedProps, targetProps));
      }
    } else if (allowDrag && isPanning || allowResize && isSelecting) {
      if (helpers_exports.isFunction(onBrushDomainChangeEnd)) {
        onBrushDomainChangeEnd(currentDomain, (0, import_defaults23.default)({}, mutatedProps, targetProps));
      }
    }
    return [{
      target: "parent",
      mutation: () => mutatedProps
    }];
  }
};
var BrushHelpers = {
  ...Helpers,
  onMouseDown: Helpers.onMouseDown.bind(Helpers),
  onGlobalMouseUp: Helpers.onGlobalMouseUp.bind(Helpers),
  onGlobalMouseMove: (0, import_throttle.default)(
    Helpers.onGlobalMouseMove.bind(Helpers),
    16,
    // eslint-disable-line no-magic-numbers
    {
      leading: true,
      trailing: false
    }
  )
};

// node_modules/victory-brush-container/es/victory-brush-container.js
var import_react_fast_compare4 = __toESM(require_react_fast_compare());
var VICTORY_BRUSH_CONTAINER_DEFAULT_PROPS = {
  allowDrag: true,
  allowDraw: true,
  allowResize: true,
  brushComponent: import_react40.default.createElement(Rect, null),
  brushStyle: {
    stroke: "transparent",
    fill: "black",
    fillOpacity: 0.1
  },
  handleComponent: import_react40.default.createElement(Rect, null),
  handleStyle: {
    stroke: "transparent",
    fill: "transparent"
  },
  handleWidth: 8,
  mouseMoveThreshold: 0
};
var useVictoryBrushContainer = (initialProps) => {
  const props = {
    ...VICTORY_BRUSH_CONTAINER_DEFAULT_PROPS,
    ...initialProps
  };
  const {
    children
  } = props;
  const getSelectBox = (coordinates) => {
    const {
      x: x2,
      y: y2
    } = coordinates;
    const {
      brushStyle,
      brushComponent,
      name
    } = props;
    const brushComponentStyle = brushComponent.props && brushComponent.props.style;
    const cursor = !props.allowDrag && !props.allowResize ? "auto" : "move";
    return x2[0] !== x2[1] && y2[0] !== y2[1] ? import_react40.default.cloneElement(brushComponent, {
      key: `${name}-brush`,
      width: Math.abs(x2[1] - x2[0]) || 1,
      height: Math.abs(y2[1] - y2[0]) || 1,
      x: Math.min(x2[0], x2[1]),
      y: Math.min(y2[0], y2[1]),
      cursor,
      style: (0, import_defaults24.default)({}, brushComponentStyle, brushStyle)
    }) : null;
  };
  const getCursorPointers = () => {
    const cursors = {
      yProps: "ns-resize",
      xProps: "ew-resize"
    };
    if (!props.allowResize && props.allowDrag) {
      cursors.xProps = "move";
      cursors.yProps = "move";
    } else if (!props.allowResize && !props.allowDrag) {
      cursors.xProps = "auto";
      cursors.yProps = "auto";
    }
    return cursors;
  };
  const getHandles = (domain) => {
    const {
      handleWidth,
      handleStyle,
      handleComponent,
      name
    } = props;
    const domainBox = BrushHelpers.getDomainBox(props, domain);
    const {
      x1,
      x2,
      y1,
      y2
    } = domainBox;
    const {
      top,
      bottom,
      left,
      right
    } = BrushHelpers.getHandles(props, domainBox);
    const width = Math.abs(x2 - x1) || 1;
    const height = Math.abs(y2 - y1) || 1;
    const handleComponentStyle = handleComponent.props && handleComponent.props.style || {};
    const style = (0, import_defaults24.default)({}, handleComponentStyle, handleStyle);
    const cursors = getCursorPointers();
    const yProps = {
      style,
      width,
      height: handleWidth,
      cursor: cursors.yProps
    };
    const xProps = {
      style,
      width: handleWidth,
      height,
      cursor: cursors.xProps
    };
    const handleProps = {
      top: top && Object.assign({
        x: top.x1,
        y: top.y1
      }, yProps),
      bottom: bottom && Object.assign({
        x: bottom.x1,
        y: bottom.y1
      }, yProps),
      left: left && Object.assign({
        y: left.y1,
        x: left.x1
      }, xProps),
      right: right && Object.assign({
        y: right.y1,
        x: right.x1
      }, xProps)
    };
    const handles = ["top", "bottom", "left", "right"].reduce((memo, curr) => handleProps[curr] ? memo.concat(import_react40.default.cloneElement(handleComponent, Object.assign({
      key: `${name}-handle-${curr}`
    }, handleProps[curr]))) : memo, []);
    return handles.length ? handles : null;
  };
  const getRect = () => {
    const {
      currentDomain,
      cachedBrushDomain
    } = props;
    const brushDomain = (0, import_defaults24.default)({}, props.brushDomain, props.domain);
    const domain = (0, import_react_fast_compare4.default)(brushDomain, cachedBrushDomain) ? (0, import_defaults24.default)({}, currentDomain, brushDomain) : brushDomain;
    const coordinates = selection_exports.getDomainCoordinates(props, domain);
    const selectBox = getSelectBox(coordinates);
    return selectBox ? [selectBox, getHandles(domain)] : [];
  };
  return {
    props,
    children: [...import_react40.default.Children.toArray(children), ...getRect()]
  };
};
var VictoryBrushContainer = (initialProps) => {
  const {
    props,
    children
  } = useVictoryBrushContainer(initialProps);
  return import_react40.default.createElement(VictoryContainer, props, children);
};
VictoryBrushContainer.role = "container";
VictoryBrushContainer.defaultEvents = (initialProps) => {
  const props = {
    ...VICTORY_BRUSH_CONTAINER_DEFAULT_PROPS,
    ...initialProps
  };
  const createEventHandler = (handler, isDisabled) => (
    // eslint-disable-next-line max-params
    (event, targetProps, eventKey, context) => props.disable || (isDisabled == null ? void 0 : isDisabled(targetProps)) ? {} : handler(event, {
      ...props,
      ...targetProps
    }, eventKey, context)
  );
  return [{
    target: "parent",
    eventHandlers: {
      onMouseDown: createEventHandler(BrushHelpers.onMouseDown),
      onTouchStart: createEventHandler(BrushHelpers.onMouseDown),
      onGlobalMouseMove: createEventHandler(BrushHelpers.onGlobalMouseMove, (targetProps) => !targetProps.isPanning && !targetProps.isSelecting),
      onGlobalTouchMove: createEventHandler(BrushHelpers.onGlobalMouseMove, (targetProps) => !targetProps.isPanning && !targetProps.isSelecting),
      onGlobalMouseUp: createEventHandler(BrushHelpers.onGlobalMouseUp),
      onGlobalTouchEnd: createEventHandler(BrushHelpers.onGlobalMouseUp),
      onGlobalTouchCancel: createEventHandler(BrushHelpers.onGlobalMouseUp)
    }
  }];
};

// node_modules/victory-brush-line/es/victory-brush-line.js
var import_pick4 = __toESM(require_pick());
var import_defaults25 = __toESM(require_defaults());
var import_react41 = __toESM(require_react());
var import_react_fast_compare5 = __toESM(require_react_fast_compare());
var SMALL_NUMBER = 1 / Number.MAX_SAFE_INTEGER;
var getScale3 = (props) => {
  const {
    scale = {},
    dimension = "x"
  } = props;
  if (scale[dimension]) {
    return scale[dimension];
  }
  const fallbackScale = scale_exports.getBaseScale(props, dimension);
  const range3 = helpers_exports.getRange(props, dimension);
  const domain = domain_exports.getDomainFromProps(props, dimension) || [0, 1];
  fallbackScale.range(range3).domain(domain);
  return fallbackScale;
};
var getDimension = (props) => {
  const {
    horizontal,
    dimension = "x"
  } = props;
  if (!horizontal) {
    return dimension;
  }
  return dimension === "x" ? "y" : "x";
};
var toRange = (props, domain) => {
  const scale = getScale3(props);
  return [scale(Math.min(...domain)), scale(Math.max(...domain))];
};
var toDomain = (props, range3) => {
  const scale = getScale3(props);
  return [scale.invert(Math.min(...range3)), scale.invert(Math.max(...range3))];
};
var getFullRange = (props) => {
  const scale = getScale3(props);
  return scale.range();
};
var getFullDomain = (props) => {
  const scale = getScale3(props);
  return scale.domain();
};
var withinBound = (value, bound) => {
  return value >= collection_exports.getMinValue(bound) && value <= collection_exports.getMaxValue(bound);
};
var getBrushDomain = (brushDomain, fullDomain) => {
  if (brushDomain) {
    const brushMin = collection_exports.getMinValue(brushDomain);
    const brushMax = collection_exports.getMaxValue(brushDomain);
    const domainMin = collection_exports.getMinValue(fullDomain);
    const domainMax = collection_exports.getMaxValue(fullDomain);
    const defaultMin = brushMin < domainMin ? domainMin : Number(domainMax) - SMALL_NUMBER;
    const defaultMax = brushMax > domainMax ? domainMax : Number(domainMin) + SMALL_NUMBER;
    const min2 = withinBound(brushMin, fullDomain) ? brushMin : defaultMin;
    const max2 = withinBound(brushMax, fullDomain) ? brushMax : defaultMax;
    return [min2, max2];
  }
  return fullDomain;
};
var getActiveHandle = (props, position, range3) => {
  const width = props.handleWidth / 2;
  const dimension = getDimension(props);
  const getHandle = (type) => {
    const base = {
      min: dimension === "x" ? Math.min(...range3) : Math.max(...range3),
      max: dimension === "x" ? Math.max(...range3) : Math.min(...range3)
    };
    return [base[type] - width, base[type] + width];
  };
  const active = ["min", "max"].reduce((memo, type) => {
    memo[type] = withinBound(position, getHandle(type)) ? type : void 0;
    return memo;
  }, {});
  return active.min && active.max ? "both" : active.min || active.max;
};
var getMinimumDomain = () => {
  return [0, SMALL_NUMBER];
};
var panBox = (props, position) => {
  const {
    brushDomain,
    startPosition
  } = props;
  const range3 = toRange(props, brushDomain);
  const fullRange = getFullRange(props);
  const size = Math.abs(range3[1] - range3[0]);
  const globalMin = Math.min(...fullRange);
  const globalMax = Math.max(...fullRange);
  const delta = startPosition ? startPosition - position : 0;
  const min2 = Math.min(...range3) - delta;
  const max2 = Math.max(...range3) - delta;
  const constrainedMin = min2 > globalMax - size ? globalMax - size : Math.max(min2, globalMin);
  const constrainedMax = max2 < globalMin + size ? globalMin + size : Math.min(max2, globalMax);
  return [constrainedMin, constrainedMax];
};
var fallbackProps5 = {
  brushAreaStyle: {
    stroke: "none",
    fill: "black",
    opacity: (_ref) => {
      let {
        active
      } = _ref;
      return active ? 0.2 : 0.1;
    }
    // eslint-disable-line no-magic-numbers
  },
  brushStyle: {
    pointerEvents: "none",
    stroke: "none",
    fill: "black",
    opacity: (_ref2) => {
      let {
        active
      } = _ref2;
      return active ? 0.4 : 0.3;
    }
    // eslint-disable-line no-magic-numbers
  },
  handleStyle: {
    pointerEvents: "none",
    stroke: "none",
    fill: "none"
  }
};
var VictoryBrushLine = class extends import_react41.default.Component {
  getRectDimensions(props, brushWidth, domain) {
    const {
      brushDomain
    } = props;
    const dimension = getDimension(props);
    const range3 = toRange(props, domain || getBrushDomain(brushDomain, getFullDomain(props)));
    const coordinates = dimension === "x" ? {
      y1: props.y1,
      y2: props.y2,
      x1: Math.min(...range3),
      x2: Math.max(...range3)
    } : {
      x1: props.x1,
      x2: props.x2,
      y1: Math.min(...range3),
      y2: Math.max(...range3)
    };
    const {
      x1,
      x2,
      y1,
      y2
    } = coordinates;
    const offset = {
      x: dimension === "x" ? 0 : brushWidth / 2,
      y: dimension === "y" ? 0 : brushWidth / 2
    };
    const x3 = Math.min(x1, x2) - offset.x;
    const y3 = Math.min(y1, y2) - offset.y;
    const width = Math.max(x1, x2) + offset.x - x3;
    const height = Math.max(y1, y2) + offset.y - y3;
    return {
      x: x3,
      y: y3,
      width,
      height
    };
  }
  getHandleDimensions(props) {
    const {
      handleWidth,
      x1,
      x2,
      y1,
      y2,
      brushDomain
    } = props;
    const dimension = getDimension(props);
    const brushWidth = props.brushWidth || props.width;
    const domain = getBrushDomain(brushDomain, getFullDomain(props));
    const range3 = toRange(props, domain);
    const defaultX = Math.min(x1, x2) - brushWidth / 2;
    const defaultY = Math.min(y1, y2) - brushWidth / 2;
    const x3 = {
      min: dimension === "x" ? Math.min(...range3) - handleWidth / 2 : defaultX,
      max: dimension === "x" ? Math.max(...range3) - handleWidth / 2 : defaultX
    };
    const y3 = {
      min: dimension === "y" ? Math.max(...range3) - handleWidth / 2 : defaultY,
      max: dimension === "y" ? Math.min(...range3) - handleWidth / 2 : defaultY
    };
    const width = dimension === "x" ? handleWidth : brushWidth;
    const height = dimension === "x" ? brushWidth : handleWidth;
    return {
      min: {
        x: x3.min,
        y: y3.min,
        width,
        height
      },
      max: {
        x: x3.max,
        y: y3.max,
        width,
        height
      }
    };
  }
  getCursor(props) {
    const {
      activeBrushes = {}
    } = props;
    const dimension = getDimension(props);
    if (activeBrushes.minHandle || activeBrushes.maxHandle) {
      return dimension === "x" ? "ew-resize" : "ns-resize";
    } else if (activeBrushes.brush) {
      return "move";
    }
    return "crosshair";
  }
  renderHandles(props) {
    const {
      handleComponent,
      handleStyle,
      id,
      brushDomain,
      datum = {},
      activeBrushes = {}
    } = props;
    if (!brushDomain) {
      return null;
    }
    const handleDimensions = this.getHandleDimensions(props);
    const style = Object.assign({}, fallbackProps5.handleStyle, handleStyle);
    const minDatum = Object.assign({
      handleValue: collection_exports.getMinValue(brushDomain)
    }, datum);
    const maxDatum = Object.assign({
      handleValue: collection_exports.getMaxValue(brushDomain)
    }, datum);
    const minHandleProps = Object.assign({
      key: `${id}-min`,
      style: helpers_exports.evaluateStyle(style, {
        datum: minDatum,
        active: activeBrushes.minHandle
      })
    }, handleDimensions.min);
    const maxHandleProps = Object.assign({
      key: `${id}-max`,
      style: helpers_exports.evaluateStyle(style, {
        datum: maxDatum,
        active: activeBrushes.maxHandle
      })
    }, handleDimensions.max);
    return [import_react41.default.cloneElement(handleComponent, minHandleProps), import_react41.default.cloneElement(handleComponent, maxHandleProps)];
  }
  renderBrush(props) {
    const {
      brushComponent,
      brushStyle,
      activeBrushes = {},
      datum = {},
      brushDomain
    } = props;
    if (!brushDomain) {
      return null;
    }
    const brushWidth = props.brushWidth || props.width;
    const rectDimensions = this.getRectDimensions(props, brushWidth);
    const baseStyle = Object.assign({}, fallbackProps5.brushStyle, brushStyle);
    const style = helpers_exports.evaluateStyle(baseStyle, {
      datum,
      active: activeBrushes.brush
    });
    const brushProps = Object.assign({
      style
    }, rectDimensions);
    return import_react41.default.cloneElement(brushComponent, brushProps);
  }
  renderBrushArea(props) {
    const {
      brushAreaComponent,
      brushAreaStyle,
      activeBrushes = {},
      datum = {}
    } = props;
    const brushAreaWidth = props.brushAreaWidth || props.width;
    const cursor = this.getCursor(props);
    const rectDimensions = this.getRectDimensions(props, brushAreaWidth, getFullDomain(props));
    const baseStyle = Object.assign({
      cursor
    }, fallbackProps5.brushAreaStyle, brushAreaStyle);
    const style = helpers_exports.evaluateStyle(baseStyle, {
      datum,
      active: activeBrushes.brushArea
    });
    const brushAreaProps = Object.assign({
      style
    }, rectDimensions);
    return import_react41.default.cloneElement(brushAreaComponent, brushAreaProps);
  }
  renderLine(props) {
    const filteredProps = (0, import_pick4.default)(props, ["x1", "x2", "y1", "y2", "datum", "scale", "active", "style"]);
    return import_react41.default.cloneElement(props.lineComponent, filteredProps);
  }
  render() {
    return import_react41.default.createElement("g", this.props.events, this.renderLine(this.props), this.renderBrushArea(this.props), this.renderBrush(this.props), this.renderHandles(this.props));
  }
};
__publicField(VictoryBrushLine, "defaultProps", {
  allowDrag: true,
  allowDraw: true,
  allowResize: true,
  brushAreaComponent: import_react41.default.createElement(Border, null),
  brushComponent: import_react41.default.createElement(Border, null),
  groupComponent: import_react41.default.createElement("g", null),
  handleComponent: import_react41.default.createElement(Border, null),
  handleWidth: 10,
  lineComponent: import_react41.default.createElement(LineSegment, null),
  width: 10
});
__publicField(VictoryBrushLine, "defaultEvents", function(props) {
  return props.disable ? void 0 : [{
    target: props.type,
    eventHandlers: {
      onMouseEnter: (evt, targetProps) => {
        evt.preventDefault();
        const {
          allowResize,
          brushDomain
        } = targetProps;
        const dimension = getDimension(targetProps);
        const parentSVG = targetProps.parentSVG || selection_exports.getParentSVG(evt);
        const position = selection_exports.getSVGEventCoordinates(evt, parentSVG)[dimension];
        const fullDomain = getFullDomain(targetProps);
        const currentDomain = getBrushDomain(brushDomain, fullDomain);
        const range3 = toRange(targetProps, currentDomain);
        const activeHandle = allowResize && getActiveHandle(targetProps, position, range3);
        const activeBrushes = {
          brushArea: !targetProps.brushDomain,
          brush: withinBound(position, range3) && !(0, import_react_fast_compare5.default)(fullDomain, currentDomain),
          minHandle: activeHandle === "min" || activeHandle === "both",
          maxHandle: activeHandle === "min" || activeHandle === "both"
        };
        return [{
          mutation: () => ({
            activeBrushes,
            brushDomain: targetProps.brushDomain,
            parentSVG
          })
        }];
      },
      onMouseDown: (evt, targetProps) => {
        evt.preventDefault();
        const {
          allowResize,
          allowDrag,
          allowDraw,
          activeBrushes,
          brushDomain
        } = targetProps;
        const dimension = getDimension(targetProps);
        if (!allowResize && !allowDrag) {
          return [];
        }
        const fullDomain = getFullDomain(targetProps);
        const currentDomain = getBrushDomain(brushDomain, fullDomain);
        const parentSVG = targetProps.parentSVG || selection_exports.getParentSVG(evt);
        const position = selection_exports.getSVGEventCoordinates(evt, parentSVG)[dimension];
        const range3 = toRange(targetProps, currentDomain);
        const activeHandle = allowResize && getActiveHandle(targetProps, position, range3);
        if (activeHandle) {
          return [{
            mutation: () => {
              return {
                parentSVG,
                isSelecting: true,
                activeHandle,
                brushDomain: currentDomain,
                startPosition: position,
                activeBrushes
              };
            }
          }];
        } else if (withinBound(position, range3) && !(0, import_react_fast_compare5.default)(fullDomain, currentDomain)) {
          return [{
            mutation: () => ({
              isPanning: allowDrag,
              startPosition: position,
              brushDomain: currentDomain,
              activeBrushes,
              parentSVG
            })
          }];
        }
        return allowDraw ? [{
          mutation: () => ({
            isSelecting: allowResize,
            brushDomain: null,
            startPosition: position,
            activeBrushes,
            parentSVG
          })
        }] : [];
      },
      // eslint-disable-next-line max-statements, complexity
      onMouseMove: (evt, targetProps) => {
        const {
          isPanning,
          isSelecting,
          allowResize,
          allowDrag,
          onBrushDomainChange,
          brushDomain
        } = targetProps;
        const dimension = getDimension(targetProps);
        if (isPanning || isSelecting) {
          evt.preventDefault();
          evt.stopPropagation();
        }
        const parentSVG = targetProps.parentSVG || selection_exports.getParentSVG(evt);
        const position = selection_exports.getSVGEventCoordinates(evt, parentSVG)[dimension];
        const fullDomain = getFullDomain(targetProps);
        const domain = getBrushDomain(brushDomain, fullDomain);
        const initialRange = toRange(targetProps, domain);
        const activeHandle = getActiveHandle(targetProps, position, initialRange);
        const activeBrushes = {
          brushArea: !targetProps.brushDomain,
          brush: withinBound(position, initialRange) && !(0, import_react_fast_compare5.default)(fullDomain, domain),
          minHandle: activeHandle === "min" || activeHandle === "both",
          maxHandle: activeHandle === "max" || activeHandle === "both"
        };
        if (!targetProps.isPanning && !targetProps.isSelecting) {
          return [{
            mutation: () => ({
              activeBrushes,
              brushDomain: targetProps.brushDomain,
              parentSVG
            })
          }];
        }
        if (allowDrag && isPanning) {
          const fullRange = getFullRange(targetProps);
          const range3 = panBox(targetProps, position);
          const currentDomain = toDomain(targetProps, range3);
          const startPosition = Math.max(...range3) >= Math.max(...fullRange) || Math.min(...range3) <= Math.min(...fullRange) ? targetProps.startPosition : position;
          const mutatedProps = {
            startPosition,
            isPanning: true,
            brushDomain: currentDomain,
            activeBrushes: {
              brush: true
            },
            parentSVG
          };
          if (helpers_exports.isFunction(onBrushDomainChange)) {
            onBrushDomainChange(currentDomain, (0, import_defaults25.default)({}, mutatedProps, targetProps));
          }
          return [{
            mutation: () => mutatedProps
          }];
        } else if (allowResize && isSelecting) {
          let currentDomain = brushDomain || getMinimumDomain();
          const range3 = toRange(targetProps, currentDomain);
          const oppositeHandle = targetProps.activeHandle === "min" ? "max" : "min";
          const handle = targetProps.activeHandle && getActiveHandle(targetProps, position, range3) === "both" ? oppositeHandle : targetProps.activeHandle;
          if (!handle) {
            currentDomain = toDomain(targetProps, [targetProps.startPosition, position]);
          } else {
            const rangeMax = dimension === "x" ? Math.max(...range3) : Math.min(...range3);
            const rangeMin = dimension === "x" ? Math.min(...range3) : Math.max(...range3);
            const min2 = handle === "max" ? rangeMin : position;
            const max2 = handle === "min" ? rangeMax : position;
            currentDomain = toDomain(targetProps, [min2, max2]);
          }
          const mutatedProps = {
            brushDomain: currentDomain,
            startPosition: targetProps.startPosition,
            isSelecting,
            activeHandle: handle,
            parentSVG,
            activeBrushes: {
              brush: true,
              minHandle: activeHandle === "min",
              maxHandle: activeHandle === "max"
            }
          };
          if (helpers_exports.isFunction(onBrushDomainChange)) {
            onBrushDomainChange(currentDomain, (0, import_defaults25.default)({}, mutatedProps, targetProps));
          }
          return [{
            mutation: () => mutatedProps
          }];
        }
        return [];
      },
      onMouseUp: (evt, targetProps) => {
        const {
          onBrushDomainChange,
          brushDomain,
          allowResize,
          activeBrushes
        } = targetProps;
        const mutatedProps = {
          isPanning: false,
          isSelecting: false,
          activeHandle: null,
          startPosition: null,
          brushDomain,
          activeBrushes
        };
        if (allowResize && helpers_exports.isFunction(onBrushDomainChange)) {
          onBrushDomainChange(brushDomain, (0, import_defaults25.default)({}, mutatedProps, targetProps));
        }
        return [{
          mutation: () => mutatedProps
        }];
      },
      onMouseLeave: (evt, targetProps) => {
        const {
          brushDomain
        } = targetProps;
        return [{
          mutation: () => ({
            isPanning: false,
            isSelecting: false,
            activeHandle: null,
            startPosition: null,
            brushDomain,
            activeBrushes: {}
          })
        }];
      }
    }
  }];
});

// node_modules/victory-candlestick/es/victory-candlestick.js
var import_react43 = __toESM(require_react());

// node_modules/victory-candlestick/es/candle.js
var import_defaults26 = __toESM(require_defaults());
var import_react42 = __toESM(require_react());
var getCandleWidth = (candleWidth, props) => {
  const {
    style
  } = props;
  if (candleWidth) {
    return helpers_exports.isFunction(candleWidth) ? helpers_exports.evaluateProp(candleWidth, props) : candleWidth;
  } else if (style.width) {
    return style.width;
  }
  return candleWidth;
};
var getCandleProps = (props, style) => {
  const {
    id,
    x: x2,
    close,
    open,
    horizontal,
    candleWidth
  } = props;
  const candleLength = Math.abs(close - open);
  return {
    key: `${id}-candle`,
    style: helpers_exports.omit(style, ["width"]),
    x: horizontal ? Math.min(open, close) : x2 - candleWidth / 2,
    y: horizontal ? x2 - candleWidth / 2 : Math.min(open, close),
    width: horizontal ? candleLength : candleWidth,
    height: horizontal ? candleWidth : candleLength
  };
};
var getHighWickProps = (props, style) => {
  const {
    horizontal,
    high,
    open,
    close,
    x: x2,
    id
  } = props;
  return {
    key: `${id}-highWick`,
    style: helpers_exports.omit(style, ["width"]),
    x1: horizontal ? high : x2,
    x2: horizontal ? Math.max(open, close) : x2,
    y1: horizontal ? x2 : high,
    y2: horizontal ? x2 : Math.min(open, close)
  };
};
var getLowWickProps = (props, style) => {
  const {
    horizontal,
    low,
    open,
    close,
    x: x2,
    id
  } = props;
  return {
    key: `${id}-lowWick`,
    style: helpers_exports.omit(style, ["width"]),
    x1: horizontal ? Math.min(open, close) : x2,
    x2: horizontal ? low : x2,
    y1: horizontal ? x2 : Math.max(open, close),
    y2: horizontal ? x2 : low
  };
};
var evaluateProps10 = (props) => {
  const style = helpers_exports.evaluateStyle(Object.assign({
    stroke: "black"
  }, props.style), props);
  const candleWidth = getCandleWidth(props.candleWidth, Object.assign({}, props, {
    style
  }));
  const ariaLabel = helpers_exports.evaluateProp(props.ariaLabel, props);
  const desc = helpers_exports.evaluateProp(props.desc, props);
  const id = helpers_exports.evaluateProp(props.id, props);
  const tabIndex = helpers_exports.evaluateProp(props.tabIndex, props);
  return Object.assign({}, props, {
    ariaLabel,
    style,
    candleWidth,
    desc,
    id,
    tabIndex
  });
};
var defaultProps12 = {
  groupComponent: import_react42.default.createElement("g", null),
  lineComponent: import_react42.default.createElement(Line, null),
  rectComponent: import_react42.default.createElement(Rect, null),
  role: "presentation",
  shapeRendering: "auto"
};
var Candle = (props) => {
  const modifiedProps = evaluateProps10((0, import_defaults26.default)({}, props, defaultProps12));
  const {
    ariaLabel,
    events,
    groupComponent,
    clipPath,
    rectComponent,
    lineComponent,
    role,
    shapeRendering,
    className,
    wickStrokeWidth,
    transform,
    style,
    desc,
    tabIndex
  } = modifiedProps;
  const wickStyle = (0, import_defaults26.default)({
    strokeWidth: wickStrokeWidth
  }, style);
  const sharedProps = {
    ...events,
    "aria-label": ariaLabel,
    role,
    shapeRendering,
    className,
    transform,
    clipPath,
    desc,
    tabIndex
  };
  const candleProps = Object.assign(getCandleProps(modifiedProps, style), sharedProps);
  const highWickProps = Object.assign(getHighWickProps(modifiedProps, wickStyle), sharedProps);
  const lowWickProps = Object.assign(getLowWickProps(modifiedProps, wickStyle), sharedProps);
  return import_react42.default.cloneElement(groupComponent, {}, [import_react42.default.cloneElement(rectComponent, candleProps), import_react42.default.cloneElement(lineComponent, highWickProps), import_react42.default.cloneElement(lineComponent, lowWickProps)]);
};

// node_modules/victory-candlestick/es/helper-methods.js
var import_isPlainObject7 = __toESM(require_isPlainObject());
var import_defaults27 = __toESM(require_defaults());
var TYPES2 = ["close", "open", "high", "low"];
var DEFAULT_CANDLE_WIDTH = 8;
var getData4 = (props) => {
  const accessorTypes = ["x", "high", "low", "close", "open"];
  return data_exports.formatData(props.data, props, accessorTypes);
};
var reduceData = (dataset, axis, type) => {
  const yDataTypes = {
    min: "_low",
    max: "_high"
  };
  const dataType = axis === "x" ? "_x" : yDataTypes[type];
  const baseCondition = type === "min" ? Infinity : -Infinity;
  return dataset.reduce((memo, datum) => {
    const current = datum[dataType];
    return memo < current && type === "min" || memo > current && type === "max" ? memo : current;
  }, baseCondition);
};
var getDomainFromData4 = (props, axis) => {
  const minDomain = domain_exports.getMinFromProps(props, axis);
  const maxDomain = domain_exports.getMaxFromProps(props, axis);
  const dataset = getData4(props);
  if (dataset.length < 1) {
    return minDomain !== void 0 && maxDomain !== void 0 ? domain_exports.getDomainFromMinMax(minDomain, maxDomain) : void 0;
  }
  const min2 = minDomain !== void 0 ? minDomain : reduceData(dataset, axis, "min");
  const max2 = maxDomain !== void 0 ? maxDomain : reduceData(dataset, axis, "max");
  return domain_exports.getDomainFromMinMax(min2, max2);
};
var getDomain5 = (props, axis) => {
  return domain_exports.createDomainFunction(getDomainFromData4)(props, axis);
};
var getLabelStyle2 = (props, styleObject, namespace) => {
  const component = props[`${namespace}LabelComponent`];
  const baseStyle = styleObject[`${namespace}Labels`] || styleObject.labels;
  if (!helpers_exports.isTooltip(component)) {
    return baseStyle;
  }
  const tooltipTheme = props.theme && props.theme.tooltip || {};
  return (0, import_defaults27.default)({}, tooltipTheme.style, baseStyle);
};
var getStyles5 = function(props, style, defaultStyles2) {
  if (defaultStyles2 === void 0) {
    defaultStyles2 = {};
  }
  if (props.disableInlineStyles) {
    return {};
  }
  const width = "100%";
  const height = "100%";
  if (!style) {
    return (0, import_defaults27.default)({
      parent: {
        height,
        width
      }
    }, defaultStyles2);
  }
  const defaultParent = defaultStyles2.parent || {};
  const defaultLabels = defaultStyles2.labels || {};
  const defaultData6 = defaultStyles2.data || {};
  const labelStyle = (0, import_defaults27.default)({}, style.labels, defaultLabels);
  return {
    parent: (0, import_defaults27.default)({}, style.parent, defaultParent, {
      width,
      height
    }),
    labels: labelStyle,
    data: (0, import_defaults27.default)({}, style.data, defaultData6),
    openLabels: (0, import_defaults27.default)({}, style.openLabels, getLabelStyle2(props, defaultStyles2, "open"), labelStyle),
    closeLabels: (0, import_defaults27.default)({}, style.closeLabels, getLabelStyle2(props, defaultStyles2, "close"), labelStyle),
    lowLabels: (0, import_defaults27.default)({}, style.lowLabels, getLabelStyle2(props, defaultStyles2, "low"), labelStyle),
    highLabels: (0, import_defaults27.default)({}, style.highLabels, getLabelStyle2(props, defaultStyles2, "high"), labelStyle)
  };
};
var formatDataFromDomain2 = (datum, domain) => {
  const minDomainX = collection_exports.getMinValue(domain.x);
  const maxDomainX = collection_exports.getMaxValue(domain.x);
  const minDomainY = collection_exports.getMinValue(domain.y);
  const maxDomainY = collection_exports.getMaxValue(domain.y);
  let {
    _x,
    _low,
    _open,
    _close,
    _high
  } = datum;
  if (_x < minDomainX || _x > maxDomainX) _x = null;
  if (_low < minDomainY && _open < minDomainY && _close < minDomainY && _high < minDomainY) _low = _open = _close = _high = null;
  if (_low > maxDomainY && _open > maxDomainY && _close > maxDomainY && _high > maxDomainY) _low = _open = _close = _high = null;
  return Object.assign({}, datum, {
    _x,
    _low,
    _open,
    _close,
    _high
  });
};
var getCalculatedValues5 = (props) => {
  const {
    polar
  } = props;
  const defaultStyle2 = helpers_exports.getDefaultStyles(props, "candlestick");
  const style = getStyles5(props, props.style, defaultStyle2);
  const data = getData4(props);
  const range3 = {
    x: helpers_exports.getRange(props, "x"),
    y: helpers_exports.getRange(props, "y")
  };
  const domain = {
    x: getDomain5(props, "x"),
    y: getDomain5(props, "y")
  };
  const scale = {
    x: scale_exports.getBaseScale(props, "x").domain(domain.x).range(props.horizontal ? range3.y : range3.x),
    y: scale_exports.getBaseScale(props, "y").domain(domain.y).range(props.horizontal ? range3.x : range3.y)
  };
  const origin = polar ? props.origin || helpers_exports.getPolarOrigin(props) : void 0;
  const defaultOrientation = props.horizontal ? "top" : "right";
  const labelOrientation = props.labelOrientation || defaultOrientation;
  return {
    domain,
    data,
    scale,
    style,
    origin,
    labelOrientation
  };
};
var isTransparent = (attr) => {
  return attr === "none" || attr === "transparent";
};
var getDataStyles = function(datum, style, props) {
  if (style === void 0) {
    style = {};
  }
  if (props.disableInlineStyles) {
    return {};
  }
  const candleColor = datum._open > datum._close ? props.candleColors.negative : props.candleColors.positive;
  const fill = style.fill || candleColor;
  const strokeColor = style.stroke;
  const stroke = isTransparent(strokeColor) ? fill : strokeColor || "black";
  return Object.assign({}, style, {
    stroke,
    fill
  });
};
var getText3 = (props, type) => {
  const {
    datum,
    index,
    labels
  } = props;
  const propName = `${type}Labels`;
  const labelProp = props[propName];
  if (!labelProp && !labels) {
    return null;
  } else if (labelProp === true || labels === true) {
    const dataName = `_${type}`;
    return `${datum[dataName]}`;
  }
  return Array.isArray(labelProp) ? labelProp[index] : labelProp;
};
var getCandleWidth2 = (props, style) => {
  const {
    data,
    candleWidth,
    scale
  } = props;
  if (candleWidth) {
    return helpers_exports.isFunction(candleWidth) ? helpers_exports.evaluateProp(candleWidth, props) : candleWidth;
  } else if (style && style.width) {
    return style.width;
  }
  const range3 = scale.x.range();
  const extent2 = Math.abs(range3[1] - range3[0]);
  const candles = data.length + 2;
  const candleRatio = props.candleRatio || 0.5;
  const defaultWidth = candleRatio * (data.length < 2 ? DEFAULT_CANDLE_WIDTH : extent2 / candles);
  return Math.max(1, defaultWidth);
};
var getOrientation3 = function(labelOrientation, type) {
  if (type === void 0) {
    type = "labels";
  }
  return (0, import_isPlainObject7.default)(labelOrientation) ? labelOrientation[type] : labelOrientation;
};
var calculatePlotValues = (props) => {
  const {
    positions,
    labelStyle,
    x: x2,
    horizontal,
    computedType,
    candleWidth,
    orientation
  } = props;
  positions.labels = (positions.open + positions.close) / 2;
  const signX = orientation === "left" ? -1 : 1;
  const signY = orientation === "top" ? -1 : 1;
  if (horizontal) {
    const yValue2 = x2;
    const xValue2 = positions[computedType];
    const dy2 = orientation === "top" || orientation === "bottom" ? signY * (candleWidth / 2) + signY * (labelStyle.padding || 0) : 0;
    const dx2 = orientation === "top" || orientation === "bottom" ? 0 : signX * (labelStyle.padding || 1);
    return {
      yValue: yValue2,
      xValue: xValue2,
      dx: dx2,
      dy: dy2
    };
  }
  const xValue = x2;
  const yValue = positions[computedType];
  const dy = orientation === "top" || orientation === "bottom" ? signY * (labelStyle.padding || 1) : 0;
  const dx = orientation === "top" || orientation === "bottom" ? 0 : signX * (candleWidth / 2) + signX * (labelStyle.padding || 0);
  return {
    yValue,
    xValue,
    dx,
    dy
  };
};
var getLabelProps2 = (props, text, style, type) => {
  const {
    x: x2,
    high,
    low,
    open,
    close,
    index,
    scale,
    datum,
    data,
    horizontal,
    candleWidth,
    labelOrientation,
    theme
  } = props;
  const component = props[`${type}LabelComponent`] || props.labelComponent;
  const defaultOrientation = horizontal ? "top" : "right";
  const orientation = component.props && component.props.orientation || getOrientation3(labelOrientation, type) || defaultOrientation;
  const positions = {
    high,
    low,
    open,
    close
  };
  const namespace = type ? `${type}Labels` : "labels";
  const labelStyle = style[namespace] || style.labels;
  const defaultVerticalAnchors = {
    top: "end",
    bottom: "start",
    left: "middle",
    right: "middle"
  };
  const defaultTextAnchors = {
    left: "end",
    right: "start",
    top: "middle",
    bottom: "middle"
  };
  const computedType = type ? type : "labels";
  const plotProps = {
    positions,
    labelStyle,
    x: x2,
    horizontal,
    computedType,
    candleWidth,
    orientation
  };
  const {
    yValue,
    xValue,
    dx,
    dy
  } = calculatePlotValues(plotProps);
  const labelProps = {
    style: labelStyle,
    y: yValue,
    x: xValue,
    dx,
    dy,
    text,
    index,
    scale,
    datum,
    data,
    orientation,
    textAnchor: labelStyle.textAnchor || defaultTextAnchors[orientation],
    verticalAnchor: labelStyle.verticalAnchor || defaultVerticalAnchors[orientation],
    angle: labelStyle.angle,
    horizontal
  };
  if (!helpers_exports.isTooltip(component)) {
    return labelProps;
  }
  const tooltipTheme = theme && theme.tooltip || {};
  return (0, import_defaults27.default)({}, labelProps, helpers_exports.omit(tooltipTheme, ["style"]));
};
var getBaseProps5 = (initialProps, fallbackProps22) => {
  const props = helpers_exports.modifyProps(initialProps, fallbackProps22, "candlestick");
  const calculatedValues = getCalculatedValues5(props);
  const {
    data,
    style,
    scale,
    domain,
    origin,
    labelOrientation
  } = calculatedValues;
  const {
    groupComponent,
    width,
    height,
    padding: padding2,
    standalone,
    name,
    candleWidth,
    candleRatio,
    theme,
    polar,
    wickStrokeWidth,
    labels,
    events,
    sharedEvents,
    horizontal,
    disableInlineStyles
  } = props;
  const initialChildProps = {
    parent: {
      domain,
      scale,
      width,
      height,
      data,
      standalone,
      theme,
      polar,
      origin,
      name,
      style: style.parent,
      padding: padding2,
      horizontal
    }
  };
  return data.reduce((childProps, datum, index) => {
    const eventKey = !helpers_exports.isNil(datum.eventKey) ? datum.eventKey : index;
    const x2 = scale.x(datum._x1 !== void 0 ? datum._x1 : datum._x);
    const formattedDatum = formatDataFromDomain2(datum, domain);
    const {
      _low,
      _open,
      _close,
      _high
    } = formattedDatum;
    const high = scale.y(_high);
    const close = scale.y(_close);
    const open = scale.y(_open);
    const low = scale.y(_low);
    const dataStyle = getDataStyles(formattedDatum, style.data, props);
    const dataProps = {
      x: x2,
      high,
      low,
      candleWidth,
      candleRatio,
      scale,
      data,
      datum: formattedDatum,
      groupComponent,
      index,
      style: dataStyle,
      width,
      polar,
      origin,
      wickStrokeWidth,
      open,
      close,
      horizontal,
      labelOrientation,
      disableInlineStyles
    };
    dataProps.candleWidth = getCandleWidth2(dataProps);
    const extendedProps = (0, import_defaults27.default)(Object.assign({}, dataProps), props);
    childProps[eventKey] = {
      data: dataProps
    };
    if (labels) {
      const text = label_helpers_exports.getText(props, formattedDatum, index);
      if (text !== void 0 && text !== null || labels && (events || sharedEvents)) {
        childProps[eventKey].labels = getLabelProps2(extendedProps, text, style);
      }
    }
    TYPES2.forEach((type) => {
      const labelText = getText3(extendedProps, type);
      const labelProp = props.labels || props[`${type}Labels`];
      if (labelText !== null && labelText !== void 0 || labelProp && (events || sharedEvents)) {
        const target = `${type}Labels`;
        childProps[eventKey][target] = getLabelProps2(extendedProps, labelText, style, type);
      }
    });
    return childProps;
  }, initialChildProps);
};

// node_modules/victory-candlestick/es/victory-candlestick.js
var fallbackProps6 = {
  width: 450,
  height: 300,
  padding: 50,
  candleColors: {
    positive: "#ffffff",
    negative: "#252525"
  }
};
var options4 = {
  components: [{
    name: "lowLabels"
  }, {
    name: "highLabels"
  }, {
    name: "openLabels"
  }, {
    name: "closeLabels"
  }, {
    name: "labels"
  }, {
    name: "data"
  }, {
    name: "parent",
    index: "parent"
  }]
};
var defaultData3 = [{
  x: new Date(2016, 6, 1),
  open: 5,
  close: 10,
  high: 15,
  low: 0
}, {
  x: new Date(2016, 6, 2),
  open: 10,
  close: 15,
  high: 20,
  low: 5
}, {
  x: new Date(2016, 6, 3),
  open: 15,
  close: 20,
  high: 25,
  low: 10
}, {
  x: new Date(2016, 6, 4),
  open: 20,
  close: 25,
  high: 30,
  low: 15
}, {
  x: new Date(2016, 6, 5),
  open: 25,
  close: 30,
  high: 35,
  low: 20
}, {
  x: new Date(2016, 6, 6),
  open: 30,
  close: 35,
  high: 40,
  low: 25
}, {
  x: new Date(2016, 6, 7),
  open: 35,
  close: 40,
  high: 45,
  low: 30
}, {
  x: new Date(2016, 6, 8),
  open: 40,
  close: 45,
  high: 50,
  low: 35
}];
var datumHasXandY2 = (datum) => {
  return !helpers_exports.isNil(datum._x) && !helpers_exports.isNil(datum._y);
};
var VictoryCandlestickBase = class extends import_react43.default.Component {
  constructor() {
    super(...arguments);
    __publicField(this, "shouldRenderDatum", (datum) => {
      return !helpers_exports.isNil(datum._x) && !helpers_exports.isNil(datum._high) && !helpers_exports.isNil(datum._low) && !helpers_exports.isNil(datum._close) && !helpers_exports.isNil(datum._open);
    });
  }
  static getDomain(props, axis) {
    return getDomain5(props, axis);
  }
  static getData(props) {
    return getData4(props);
  }
  static getBaseProps(props) {
    return getBaseProps5(props, fallbackProps6);
  }
  // Overridden in native versions
  shouldAnimate() {
    return !!this.props.animate;
  }
  renderCandleData(props, shouldRenderDatum) {
    if (shouldRenderDatum === void 0) {
      shouldRenderDatum = datumHasXandY2;
    }
    const {
      dataComponent,
      labelComponent,
      groupComponent
    } = props;
    const types = ["close", "open", "low", "high"];
    if (!groupComponent) {
      throw new Error("VictoryCandlestick expects a groupComponent prop");
    }
    const children = [];
    if (dataComponent) {
      const dataComponents = this.dataKeys.reduce((validDataComponents, _dataKey, index) => {
        const dataProps = this.getComponentProps(dataComponent, "data", index);
        if (shouldRenderDatum(dataProps.datum)) {
          validDataComponents.push(import_react43.default.cloneElement(dataComponent, dataProps));
        }
        return validDataComponents;
      }, []);
      children.push(...dataComponents);
    }
    const labelComponents = types.flatMap((type) => this.dataKeys.map((key, index) => {
      const name = `${type}Labels`;
      const baseComponent = props[`${type}LabelComponent`];
      const labelProps = this.getComponentProps(baseComponent, name, index);
      if (labelProps.text !== void 0 && labelProps.text !== null) {
        return import_react43.default.cloneElement(baseComponent, labelProps);
      }
      return void 0;
    }).filter((comp) => comp !== void 0));
    children.push(...labelComponents);
    if (labelComponent) {
      const labelsComponents = this.dataKeys.map((_dataKey, index) => {
        const labelProps = this.getComponentProps(labelComponent, "labels", index);
        if (labelProps.text !== void 0 && labelProps.text !== null) {
          return import_react43.default.cloneElement(labelComponent, labelProps);
        }
        return void 0;
      }).filter((comp) => comp !== void 0);
      children.push(...labelsComponents);
    }
    return this.renderContainer(groupComponent, children);
  }
  render() {
    const {
      animationWhitelist,
      role
    } = VictoryCandlestick;
    const props = helpers_exports.modifyProps(this.props, fallbackProps6, role);
    if (this.shouldAnimate()) {
      return this.animateComponent(props, animationWhitelist);
    }
    const children = this.renderCandleData(props, this.shouldRenderDatum);
    const component = props.standalone ? this.renderContainer(props.containerComponent, children) : children;
    return user_props_exports.withSafeUserProps(component, props);
  }
};
__publicField(VictoryCandlestickBase, "animationWhitelist", ["data", "domain", "height", "padding", "samples", "size", "style", "width"]);
__publicField(VictoryCandlestickBase, "displayName", "VictoryCandlestick");
__publicField(VictoryCandlestickBase, "role", "candlestick");
__publicField(VictoryCandlestickBase, "defaultTransitions", default_transitions_exports.discreteTransitions());
__publicField(VictoryCandlestickBase, "defaultProps", {
  containerComponent: import_react43.default.createElement(VictoryContainer, null),
  data: defaultData3,
  dataComponent: import_react43.default.createElement(Candle, null),
  groupComponent: import_react43.default.createElement("g", {
    role: "presentation"
  }),
  labelComponent: import_react43.default.createElement(VictoryLabel, null),
  highLabelComponent: import_react43.default.createElement(VictoryLabel, null),
  lowLabelComponent: import_react43.default.createElement(VictoryLabel, null),
  openLabelComponent: import_react43.default.createElement(VictoryLabel, null),
  closeLabelComponent: import_react43.default.createElement(VictoryLabel, null),
  samples: 50,
  sortOrder: "ascending",
  standalone: true,
  theme: VictoryTheme.grayscale
});
__publicField(VictoryCandlestickBase, "expectedComponents", ["openLabelComponent", "closeLabelComponent", "highLabelComponent", "lowLabelComponent", "dataComponent", "labelComponent", "groupComponent", "containerComponent"]);
var VictoryCandlestick = addEvents(VictoryCandlestickBase, options4);

// node_modules/victory-canvas/es/canvas-bar.js
var import_react45 = __toESM(require_react());

// node_modules/victory-canvas/es/hooks/use-canvas-context.js
var import_react44 = __toESM(require_react());
var CanvasContext = import_react44.default.createContext(void 0);
var useCanvasContext = () => {
  const context = import_react44.default.useContext(CanvasContext);
  if (!context) {
    throw new Error(`This component must be wrapped in a CanvasContext.Provider component.
      Try setting groupComponent={<CanvasGroup />} in your chart component.`);
  }
  return context;
};

// node_modules/victory-canvas/es/canvas-bar.js
var evaluateProps11 = (props) => {
  const style = getStyle2(props.style, props);
  const barWidth = getBarWidth(props.barWidth, Object.assign({}, props, {
    style
  }));
  const cornerRadius = getCornerRadius(props.cornerRadius, Object.assign({}, props, {
    style,
    barWidth
  }));
  const modifiedProps = Object.assign({}, props, {
    style,
    barWidth,
    cornerRadius
  });
  return modifiedProps;
};
var usePreviousValue = (value) => {
  const ref = import_react45.default.useRef();
  import_react45.default.useEffect(() => {
    ref.current = value;
  });
  return ref.current;
};
var CanvasBar = (props) => {
  const {
    canvasRef
  } = useCanvasContext();
  const modifiedProps = evaluateProps11(props);
  const {
    polar,
    style,
    barWidth,
    cornerRadius,
    origin
  } = modifiedProps;
  const path2d = import_react45.default.useMemo(() => {
    const p = polar ? getPolarBarPath(modifiedProps, cornerRadius) : getBarPath(modifiedProps, barWidth, cornerRadius);
    return new Path2D(p);
  }, [polar, barWidth, cornerRadius, modifiedProps]);
  const previousPath = usePreviousValue(path2d);
  const draw = import_react45.default.useCallback((ctx, path) => {
    ctx.fillStyle = style.fill;
    ctx.strokeStyle = style.stroke;
    ctx.globalAlpha = style.fillOpacity;
    ctx.lineWidth = style.strokeWidth;
    if (polar) {
      ctx.translate((origin == null ? void 0 : origin.x) || 0, (origin == null ? void 0 : origin.y) || 0);
    }
    ctx.fill(path);
    ctx.setTransform(1, 0, 0, 1, 0, 0);
  }, [style, origin, polar]);
  const clearPreviousPath = import_react45.default.useCallback((ctx) => {
    if (previousPath) {
      ctx.save();
      const strokeWidth = style.strokeWidth || 0;
      ctx.lineWidth = strokeWidth + 2;
      ctx.globalCompositeOperation = "destination-out";
      draw(ctx, previousPath);
      ctx.stroke(previousPath);
      ctx.restore();
    }
  }, [draw, previousPath, style]);
  import_react45.default.useEffect(() => {
    var _a;
    const ctx = (_a = canvasRef.current) == null ? void 0 : _a.getContext("2d");
    if (!ctx) return;
    clearPreviousPath(ctx);
    draw(ctx, path2d);
  }, [canvasRef, draw, polar, barWidth, cornerRadius, modifiedProps, path2d, clearPreviousPath]);
  return null;
};

// node_modules/victory-canvas/es/canvas-group.js
var import_react46 = __toESM(require_react());
var CanvasGroup = (props) => {
  const canvasRef = import_react46.default.useRef(null);
  const {
    children,
    width = 0,
    height = 0,
    clipWidth,
    padding: padding2
  } = props;
  const clear = import_react46.default.useCallback((ctx) => {
    return ctx.clearRect(0, 0, width, height);
  }, [width, height]);
  const clip = import_react46.default.useCallback((ctx) => {
    const paddingRight = typeof padding2 === "number" ? padding2 : (padding2 == null ? void 0 : padding2.right) || 0;
    const paddingLeft = typeof padding2 === "number" ? padding2 : (padding2 == null ? void 0 : padding2.left) || 0;
    const maxClipWidth = width - paddingRight - paddingLeft;
    ctx.clearRect(width - paddingRight, 0, clipWidth ? (maxClipWidth - clipWidth) * -1 : 0, height);
  }, [width, height, padding2, clipWidth]);
  return import_react46.default.createElement(CanvasContext.Provider, {
    value: {
      canvasRef,
      clear,
      clip
    }
  }, import_react46.default.createElement("foreignObject", {
    width,
    height,
    x: 0,
    y: 0
  }, import_react46.default.createElement("canvas", {
    width,
    height,
    ref: canvasRef
  })), children);
};
CanvasGroup.role = "container";

// node_modules/victory-canvas/es/canvas-curve.js
var import_react47 = __toESM(require_react());
var CanvasCurve = (props) => {
  const {
    canvasRef,
    clear,
    clip
  } = useCanvasContext();
  const {
    style,
    data
  } = props;
  const {
    stroke,
    strokeWidth
  } = style;
  const draw = import_react47.default.useCallback((ctx) => {
    const line = line_helpers_exports.getLineFunction(props);
    ctx.strokeStyle = stroke;
    ctx.lineWidth = strokeWidth;
    line.context(ctx)(data);
    ctx.stroke();
  }, [data, props, stroke, strokeWidth]);
  import_react47.default.useEffect(() => {
    var _a;
    const ctx = (_a = canvasRef.current) == null ? void 0 : _a.getContext("2d");
    if (!ctx) return;
    clear(ctx);
    draw(ctx);
    clip(ctx);
  }, [canvasRef, draw, clear, clip]);
  return null;
};

// node_modules/victory-canvas/es/canvas-point.js
var import_react48 = __toESM(require_react());
var getPath2 = (props) => {
  const {
    x: x2,
    y: y2,
    size,
    symbol
  } = props;
  if (props.getPath) {
    return props.getPath(x2, y2, size);
  }
  const pathFunctions = {
    circle: point_path_helpers_exports.circle,
    square: point_path_helpers_exports.square,
    diamond: point_path_helpers_exports.diamond,
    triangleDown: point_path_helpers_exports.triangleDown,
    triangleUp: point_path_helpers_exports.triangleUp,
    plus: point_path_helpers_exports.plus,
    minus: point_path_helpers_exports.minus,
    star: point_path_helpers_exports.star,
    cross: point_path_helpers_exports.cross
  };
  const symbolFunction = typeof pathFunctions[symbol] === "function" ? pathFunctions[symbol] : pathFunctions.circle;
  return symbolFunction(x2, y2, size);
};
var evaluateProps12 = (props) => {
  const size = helpers_exports.evaluateProp(props.size, props);
  const style = helpers_exports.evaluateStyle(props.style, props);
  const symbol = helpers_exports.evaluateProp(props.symbol, props);
  return Object.assign({}, props, {
    size,
    style,
    symbol
  });
};
var CanvasPoint = (props) => {
  const {
    canvasRef
  } = useCanvasContext();
  const modifiedProps = evaluateProps12(props);
  const draw = import_react48.default.useCallback((ctx) => {
    const {
      style
    } = modifiedProps;
    const path = getPath2(modifiedProps);
    ctx.fillStyle = style.fill;
    const path2d = new Path2D(path);
    ctx.fill(path2d);
  }, [modifiedProps]);
  import_react48.default.useEffect(() => {
    var _a;
    const ctx = (_a = canvasRef.current) == null ? void 0 : _a.getContext("2d");
    if (!ctx) return;
    draw(ctx);
  }, []);
  return null;
};

// node_modules/victory-chart/es/victory-chart.js
var import_isEmpty8 = __toESM(require_isEmpty());
var import_defaults31 = __toESM(require_defaults());
var import_react52 = __toESM(require_react());

// node_modules/victory-shared-events/es/victory-shared-events.js
var import_fromPairs = __toESM(require_fromPairs());
var import_isEmpty6 = __toESM(require_isEmpty());
var import_defaults28 = __toESM(require_defaults());
var import_react49 = __toESM(require_react());
var import_react_fast_compare6 = __toESM(require_react_fast_compare());
var import_json_stringify_safe = __toESM(require_stringify());
var VictorySharedEvents = class extends import_react49.default.Component {
  constructor(props) {
    super(props);
    this.getScopedEvents = events_exports.getScopedEvents.bind(this);
    this.getEventState = events_exports.getEventState.bind(this);
    this.state = this.state || {};
    this.sharedEventsCache = {};
    this.globalEvents = {};
    this.prevGlobalEventKeys = [];
    this.boundGlobalEvents = {};
    this.baseProps = this.getBaseProps(props);
  }
  shouldComponentUpdate(nextProps) {
    if (!(0, import_react_fast_compare6.default)(this.props, nextProps)) {
      this.baseProps = this.getBaseProps(nextProps);
      const externalMutations = this.getExternalMutations(nextProps, this.baseProps);
      this.applyExternalMutations(nextProps, externalMutations);
    }
    return true;
  }
  componentDidMount() {
    const globalEventKeys = Object.keys(this.globalEvents);
    globalEventKeys.forEach((key) => this.addGlobalListener(key));
    this.prevGlobalEventKeys = globalEventKeys;
  }
  componentDidUpdate() {
    const globalEventKeys = Object.keys(this.globalEvents);
    const removedGlobalEventKeys = collection_exports.difference(this.prevGlobalEventKeys, globalEventKeys);
    removedGlobalEventKeys.forEach((key) => this.removeGlobalListener(key));
    const addedGlobalEventKeys = collection_exports.difference(globalEventKeys, this.prevGlobalEventKeys);
    addedGlobalEventKeys.forEach((key) => this.addGlobalListener(key));
    this.prevGlobalEventKeys = globalEventKeys;
  }
  componentWillUnmount() {
    this.prevGlobalEventKeys.forEach((key) => this.removeGlobalListener(key));
  }
  addGlobalListener(key) {
    const boundListener = (event) => {
      const listener = this.globalEvents[key];
      return listener && listener(events_exports.emulateReactEvent(event));
    };
    this.boundGlobalEvents[key] = boundListener;
    window.addEventListener(events_exports.getGlobalEventNameFromKey(key), boundListener);
  }
  removeGlobalListener(key) {
    window.removeEventListener(events_exports.getGlobalEventNameFromKey(key), this.boundGlobalEvents[key]);
  }
  getAllEvents(props) {
    const components = ["container", "groupComponent"];
    const componentEvents = events_exports.getComponentEvents(props, components);
    if (Array.isArray(componentEvents)) {
      return Array.isArray(props.events) ? componentEvents.concat(...props.events) : componentEvents;
    }
    return props.events;
  }
  applyExternalMutations(props, externalMutations) {
    if (!(0, import_isEmpty6.default)(externalMutations)) {
      const callbacks = props.externalEventMutations.reduce((memo, mutation) => helpers_exports.isFunction(mutation.callback) ? memo.concat(mutation.callback) : memo, []);
      const compiledCallbacks = callbacks.length ? () => {
        callbacks.forEach((c) => c());
      } : void 0;
      this.setState(externalMutations, compiledCallbacks);
    }
  }
  getExternalMutations(props, baseProps3) {
    return !(0, import_isEmpty6.default)(props.externalEventMutations) ? events_exports.getExternalMutationsWithChildren(props.externalEventMutations, baseProps3, this.state, Object.keys(baseProps3)) : void 0;
  }
  cacheSharedEvents(name, sharedEvents, cacheValues) {
    this.sharedEventsCache[name] = [sharedEvents, cacheValues];
  }
  getCachedSharedEvents(name, cacheValues) {
    const [sharedEvents, prevCacheValues] = this.sharedEventsCache[name] || [];
    if (sharedEvents && (0, import_react_fast_compare6.default)(cacheValues, prevCacheValues)) {
      return sharedEvents;
    }
    return void 0;
  }
  getBaseProps(props) {
    const {
      container
    } = props;
    const children = import_react49.default.Children.toArray(this.props.children);
    const childBaseProps = this.getBasePropsFromChildren(children);
    const parentBaseProps = container ? container.props : {};
    return Object.assign({}, childBaseProps, {
      parent: parentBaseProps
    });
  }
  getBasePropsFromChildren(childComponents) {
    const iteratee = (child, childName) => {
      if (child.type && helpers_exports.isFunction(child.type.getBaseProps)) {
        const baseProps4 = child.props && child.type.getBaseProps(child.props);
        return baseProps4 ? [[childName, baseProps4]] : null;
      }
      return null;
    };
    const baseProps3 = helpers_exports.reduceChildren(childComponents, iteratee);
    return (0, import_fromPairs.default)(baseProps3);
  }
  getNewChildren(props, baseProps3) {
    const {
      events,
      eventKey
    } = props;
    const alterChildren = (children, childNames2) => {
      return children.reduce((memo, child, index) => {
        if (child.props.children) {
          const newChildren = import_react49.default.Children.toArray(child.props.children);
          const names = childNames2.slice(index, index + newChildren.length);
          const results = import_react49.default.cloneElement(child, child.props, alterChildren(newChildren, names));
          return memo.concat(results);
        } else if (childNames2[index] !== "parent" && child.type && helpers_exports.isFunction(child.type.getBaseProps)) {
          const name = child.props.name || childNames2[index];
          const childEvents = Array.isArray(events) && events.filter((event) => {
            if (event.target === "parent") {
              return false;
            }
            return Array.isArray(event.childName) ? event.childName.indexOf(name) > -1 : event.childName === name || event.childName === "all";
          });
          const sharedEventsCacheValues = [name, baseProps3, childEvents, (0, import_json_stringify_safe.default)(this.state[name])];
          const sharedEvents = this.getCachedSharedEvents(name, sharedEventsCacheValues) || {
            events: childEvents,
            // partially apply child name and baseProps,
            getEvents: (evts, target) => this.getScopedEvents(evts, target, name, baseProps3),
            // partially apply child name
            getEventState: (key, target) => this.getEventState(key, target, name)
          };
          this.cacheSharedEvents(name, sharedEvents, sharedEventsCacheValues);
          return memo.concat(import_react49.default.cloneElement(child, Object.assign({
            key: `events-${name}`,
            sharedEvents,
            eventKey,
            name
          }, child.props)));
        }
        return memo.concat(child);
      }, []);
    };
    const childNames = Object.keys(baseProps3);
    const childComponents = import_react49.default.Children.toArray(props.children);
    return alterChildren(childComponents, childNames);
  }
  getContainer(props, baseProps3, events) {
    const children = this.getNewChildren(props, baseProps3);
    const parents = Array.isArray(events) ? events.filter((event) => event.target === "parent") : [];
    const sharedEvents = parents.length > 0 ? {
      events: parents,
      // partially apply childName (null) and baseProps,
      getEvents: (evts, target) => this.getScopedEvents(evts, target, null, baseProps3),
      getEventState: this.getEventState
    } : null;
    const container = props.container || props.groupComponent;
    const role = container.type && container.type.role;
    const containerProps = container.props || {};
    const boundGetEvents = events_exports.getEvents.bind(this);
    const parentEvents = sharedEvents && boundGetEvents({
      sharedEvents
    }, "parent");
    const parentProps = (0, import_defaults28.default)({}, this.getEventState("parent", "parent"), containerProps, baseProps3.parent, {
      children
    });
    const containerEvents = (0, import_defaults28.default)({}, events_exports.getPartialEvents(parentEvents, "parent", parentProps), containerProps.events);
    this.globalEvents = events_exports.getGlobalEvents(containerEvents);
    const localEvents = events_exports.omitGlobalEvents(containerEvents);
    return role === "container" ? import_react49.default.cloneElement(container, Object.assign({}, parentProps, {
      events: localEvents
    })) : import_react49.default.cloneElement(container, localEvents, children);
  }
  render() {
    const events = this.getAllEvents(this.props);
    if (events) {
      return this.getContainer(this.props, this.baseProps, events);
    }
    return import_react49.default.cloneElement(this.props.container, {
      children: this.props.children
    });
  }
};
__publicField(VictorySharedEvents, "displayName", "VictorySharedEvents");
__publicField(VictorySharedEvents, "role", "shared-event-wrapper");
__publicField(VictorySharedEvents, "contextType", timer_context_default);
__publicField(VictorySharedEvents, "defaultProps", {
  groupComponent: import_react49.default.createElement("g", null)
});

// node_modules/victory-polar-axis/es/victory-polar-axis.js
var import_isEmpty7 = __toESM(require_isEmpty());
var import_react50 = __toESM(require_react());

// node_modules/victory-polar-axis/es/helper-methods.js
var import_defaults29 = __toESM(require_defaults());
var import_uniqBy2 = __toESM(require_uniqBy());
var getPosition4 = (r, angle, axis) => {
  return axis === "x" ? r * Math.cos(angle) : -r * Math.sin(angle);
};
var getAxisType = (props) => {
  const typicalType = props.dependentAxis ? "radial" : "angular";
  const invertedType = typicalType === "angular" ? "radial" : "angular";
  return props.horizontal ? invertedType : typicalType;
};
var filterTicks = (ticks2, scale) => {
  const compareTicks = (t) => scale(t) % (2 * Math.PI);
  return (0, import_uniqBy2.default)(ticks2, compareTicks);
};
var getEvaluatedStyles2 = (style, props) => {
  return {
    tickStyle: helpers_exports.evaluateStyle(style.ticks, props),
    labelStyle: helpers_exports.evaluateStyle(style.tickLabels, props),
    gridStyle: helpers_exports.evaluateStyle(style.grid, props)
  };
};
var getStyleObject2 = (props) => {
  var _a, _b;
  const {
    theme = {},
    dependentAxis
  } = props;
  const generalAxisStyle = theme.polarAxis && theme.polarAxis.style || theme.axis && theme.axis.style;
  const polarAxisType = dependentAxis ? "polarDependentAxis" : "polarIndependentAxis";
  const standardAxisType = dependentAxis ? "dependentAxis" : "independentAxis";
  const specificAxisStyle = ((_a = theme == null ? void 0 : theme[polarAxisType]) == null ? void 0 : _a.style) || ((_b = theme == null ? void 0 : theme[standardAxisType]) == null ? void 0 : _b.style);
  const mergeStyles = () => {
    const styleNamespaces = ["axis", "axisLabel", "grid", "parent", "tickLabels", "ticks"];
    return styleNamespaces.reduce((memo, curr) => {
      memo[curr] = (0, import_defaults29.default)({}, specificAxisStyle == null ? void 0 : specificAxisStyle[curr], generalAxisStyle == null ? void 0 : generalAxisStyle[curr]);
      return memo;
    }, {});
  };
  return generalAxisStyle && specificAxisStyle ? mergeStyles() : specificAxisStyle || generalAxisStyle;
};
var getRadius2 = (props) => {
  const {
    left,
    right,
    top,
    bottom
  } = helpers_exports.getPadding(props);
  const {
    width,
    height
  } = props;
  if (width === void 0 || height === void 0) {
    throw new Error("VictoryPolarAxis: width and height properties are required for standalone axes.");
  }
  return Math.min(width - left - right, height - top - bottom) / 2;
};
var getRange2 = (props, axis) => {
  if (props.range && props.range[axis]) {
    return props.range[axis];
  } else if (props.range && Array.isArray(props.range)) {
    return props.range;
  }
  const axisType = getAxisType(props);
  if (axisType === "angular") {
    const startAngle = helpers_exports.degreesToRadians(props.startAngle);
    const endAngle = helpers_exports.degreesToRadians(props.endAngle);
    return [startAngle, endAngle];
  }
  const radius = getRadius2(props);
  return [props.innerRadius || 0, radius];
};
var getScale4 = (props) => {
  const axis = axis_exports.getAxis(props);
  const scale = scale_exports.getBaseScale(props, axis);
  const domain = axis_exports.getDomain(props, axis) || scale.domain();
  const range3 = getRange2(props, axis);
  scale.range(range3);
  scale.domain(domain);
  return scale;
};
var getStyles6 = function(props, styleObject) {
  if (styleObject === void 0) {
    styleObject = {};
  }
  if (props.disableInlineStyles) {
    return {};
  }
  const style = props.style || {};
  const parentStyleProps = {
    height: "auto",
    width: "100%"
  };
  return {
    parent: (0, import_defaults29.default)(parentStyleProps, style.parent, styleObject.parent),
    axis: (0, import_defaults29.default)({}, style.axis, styleObject.axis),
    axisLabel: (0, import_defaults29.default)({}, style.axisLabel, styleObject.axisLabel),
    grid: (0, import_defaults29.default)({}, style.grid, styleObject.grid),
    ticks: (0, import_defaults29.default)({}, style.ticks, styleObject.ticks),
    tickLabels: (0, import_defaults29.default)({}, style.tickLabels, styleObject.tickLabels)
  };
};
var getAxisAngle = (props) => {
  const {
    axisAngle,
    startAngle,
    dependentAxis
  } = props;
  const axis = axis_exports.getAxis(props);
  const axisValue = axis_exports.getAxisValue(props, axis);
  if (axisValue === void 0 || !dependentAxis) {
    return axisAngle === void 0 ? startAngle : axisAngle;
  }
  return helpers_exports.radiansToDegrees(axisValue);
};
var getTickProps2 = (props, calculatedValues, tickValue, index) => {
  const {
    axisType,
    radius,
    scale,
    style,
    stringTicks: stringTicks2,
    ticks: ticks2,
    tickFormat: tickFormat2,
    origin
  } = calculatedValues;
  const text = tickFormat2(tickValue, index, ticks2);
  const tick = stringTicks2 ? stringTicks2[index] : tickValue;
  const {
    tickStyle
  } = getEvaluatedStyles2(style, {
    tick,
    tickValue,
    index,
    ticks: ticks2,
    stringTicks: stringTicks2,
    radius,
    scale,
    axisType,
    text
  });
  const axisAngle = axisType === "radial" ? getAxisAngle(props) : void 0;
  const tickPadding = tickStyle.padding || tickStyle.size || 0;
  const padAngle = helpers_exports.degreesToRadians(90 - axisAngle);
  const tickAngle = axisType === "angular" ? scale(tickValue) : helpers_exports.degreesToRadians(-1 * axisAngle);
  const tickRadius = axisType === "angular" ? radius : scale(tickValue);
  return axisType === "angular" ? {
    index,
    datum: tick,
    style: tickStyle,
    x1: getPosition4(tickRadius, tickAngle, "x") + origin.x,
    y1: getPosition4(tickRadius, tickAngle, "y") + origin.y,
    x2: getPosition4(tickRadius + tickPadding, tickAngle, "x") + origin.x,
    y2: getPosition4(tickRadius + tickPadding, tickAngle, "y") + origin.y
  } : {
    index,
    datum: tick,
    style: tickStyle,
    x1: tickRadius * Math.cos(tickAngle) + Math.cos(padAngle) * tickPadding + origin.x,
    x2: tickRadius * Math.cos(tickAngle) - Math.cos(padAngle) * tickPadding + origin.x,
    y1: tickRadius * Math.sin(tickAngle) + Math.sin(padAngle) * tickPadding + origin.y,
    y2: tickRadius * Math.sin(tickAngle) - Math.sin(padAngle) * tickPadding + origin.y
  };
};
var getTickLabelProps2 = (props, calculatedValues, tickValue, index) => {
  const {
    axisType,
    radius,
    tickFormat: tickFormat2,
    style,
    scale,
    ticks: ticks2,
    stringTicks: stringTicks2,
    origin
  } = calculatedValues;
  const text = tickFormat2(tickValue, index, ticks2);
  const tick = stringTicks2 ? stringTicks2[index] : tickValue;
  const {
    labelStyle
  } = getEvaluatedStyles2(style, {
    text,
    tick,
    tickValue,
    index,
    ticks: ticks2,
    stringTicks: stringTicks2,
    radius,
    scale,
    axisType
  });
  const {
    tickLabelComponent
  } = props;
  const labelPlacement = (tickLabelComponent == null ? void 0 : tickLabelComponent.props.labelPlacement) ? tickLabelComponent.props.labelPlacement : props.labelPlacement;
  const tickPadding = labelStyle.padding || 0;
  const angularPadding = 0;
  const axisAngle = axisType === "radial" ? getAxisAngle(props) : void 0;
  const labelAngle = axisType === "angular" ? helpers_exports.radiansToDegrees(scale(tickValue)) : axisAngle + angularPadding;
  const textAngle = labelStyle.angle === void 0 ? label_helpers_exports.getPolarAngle(Object.assign({}, props, {
    labelPlacement
  }), labelAngle) : labelStyle.angle;
  const labelRadius = axisType === "angular" ? radius + tickPadding : scale(tickValue);
  const textAnchor = labelStyle.textAnchor || label_helpers_exports.getPolarTextAnchor(Object.assign({}, props, {
    labelPlacement
  }), labelAngle);
  return {
    index,
    datum: tick,
    style: labelStyle,
    angle: textAngle,
    textAnchor,
    text,
    x: labelRadius * Math.cos(helpers_exports.degreesToRadians(labelAngle)) + origin.x,
    y: -labelRadius * Math.sin(helpers_exports.degreesToRadians(labelAngle)) + origin.y
  };
};
var getGridProps2 = (props, calculatedValues, tickValue, index) => {
  const {
    axisType,
    radius,
    style,
    scale,
    stringTicks: stringTicks2,
    ticks: ticks2,
    tickFormat: tickFormat2,
    origin
  } = calculatedValues;
  const text = tickFormat2(tickValue, index, ticks2);
  const {
    startAngle,
    endAngle,
    innerRadius = 0
  } = props;
  const tick = stringTicks2 ? stringTicks2[index] : tickValue;
  const {
    gridStyle
  } = getEvaluatedStyles2(style, {
    tick,
    tickValue,
    index,
    ticks: ticks2,
    stringTicks: stringTicks2,
    radius,
    scale,
    axisType,
    text
  });
  const angle = scale(tickValue);
  return axisType === "angular" ? {
    index,
    datum: tick,
    style: gridStyle,
    x1: getPosition4(radius, angle, "x") + origin.x,
    y1: getPosition4(radius, angle, "y") + origin.y,
    x2: getPosition4(innerRadius, angle, "x") + origin.x,
    y2: getPosition4(innerRadius, angle, "y") + origin.y
  } : {
    style: gridStyle,
    index,
    datum: tick,
    cx: origin.x,
    cy: origin.y,
    r: scale(tickValue),
    startAngle,
    endAngle
  };
};
var getAxisLabelProps2 = (props, calculatedValues) => {
  const {
    axisType,
    radius,
    style,
    origin
  } = calculatedValues;
  const {
    axisLabelComponent
  } = props;
  if (axisType !== "radial") {
    return {};
  }
  const labelPlacement = (axisLabelComponent == null ? void 0 : axisLabelComponent.props.labelPlacement) ? axisLabelComponent.props.labelPlacement : props.labelPlacement;
  const labelStyle = style && style.axisLabel || {};
  const axisAngle = axisType === "radial" ? getAxisAngle(props) : void 0;
  const textAngle = labelStyle.angle === void 0 ? label_helpers_exports.getPolarAngle(Object.assign({}, props, {
    labelPlacement
  }), axisAngle) : labelStyle.angle;
  const labelRadius = radius + (labelStyle.padding || 0);
  const textAnchor = labelStyle.textAnchor || label_helpers_exports.getPolarTextAnchor(Object.assign({}, props, {
    labelPlacement
  }), axisAngle);
  const verticalAnchor = labelStyle.verticalAnchor || label_helpers_exports.getPolarVerticalAnchor(Object.assign({}, props, {
    labelPlacement
  }), axisAngle);
  return {
    style: labelStyle,
    angle: textAngle,
    textAnchor,
    verticalAnchor,
    text: props.label,
    x: getPosition4(labelRadius, helpers_exports.degreesToRadians(axisAngle), "x") + origin.x,
    y: getPosition4(labelRadius, helpers_exports.degreesToRadians(axisAngle), "y") + origin.y
  };
};
var getAxisProps2 = (modifiedProps, calculatedValues) => {
  const {
    style,
    axisType,
    radius,
    origin
  } = calculatedValues;
  const {
    startAngle,
    endAngle,
    innerRadius = 0
  } = modifiedProps;
  const axisAngle = axisType === "radial" ? helpers_exports.degreesToRadians(getAxisAngle(modifiedProps)) : void 0;
  return axisType === "radial" ? {
    style: style.axis,
    x1: getPosition4(innerRadius, axisAngle, "x") + origin.x,
    x2: getPosition4(radius, axisAngle, "x") + origin.x,
    y1: getPosition4(innerRadius, axisAngle, "y") + origin.y,
    y2: getPosition4(radius, axisAngle, "y") + origin.y
  } : {
    style: style.axis,
    cx: origin.x,
    cy: origin.y,
    r: radius,
    startAngle,
    endAngle
  };
};
var getCalculatedValues6 = (initialProps) => {
  const props = Object.assign({
    polar: true
  }, initialProps);
  const defaultStyles2 = getStyleObject2(props);
  const style = getStyles6(props, defaultStyles2);
  const padding2 = helpers_exports.getPadding(props);
  const axis = axis_exports.getAxis(props);
  const axisType = getAxisType(props);
  const stringTicks2 = axis_exports.stringTicks(props) ? props.tickValues : void 0;
  const domain = axis_exports.getDomain(props, axis);
  const range3 = getRange2(props, axis);
  const scale = getScale4(props);
  const initialTicks = axis_exports.getTicks(props, scale);
  const ticks2 = axisType === "angular" ? filterTicks(initialTicks, scale) : initialTicks;
  const tickFormat2 = axis_exports.getTickFormat(props, scale);
  const radius = getRadius2(props);
  const origin = helpers_exports.getPolarOrigin(props);
  return {
    axis,
    style,
    padding: padding2,
    stringTicks: stringTicks2,
    axisType,
    scale,
    ticks: ticks2,
    tickFormat: tickFormat2,
    domain,
    range: range3,
    radius,
    origin
  };
};
var getBaseProps6 = (initialProps, fallbackProps22) => {
  const props = axis_exports.modifyProps(initialProps, fallbackProps22);
  const calculatedValues = getCalculatedValues6(props);
  const {
    style,
    scale,
    ticks: ticks2,
    domain
  } = calculatedValues;
  const {
    width,
    height,
    standalone,
    theme,
    name
  } = props;
  const axisProps = getAxisProps2(props, calculatedValues);
  const axisLabelProps = getAxisLabelProps2(props, calculatedValues);
  const initialChildProps = {
    parent: {
      style: style.parent,
      ticks: ticks2,
      scale,
      width,
      height,
      domain,
      standalone,
      theme,
      name
    }
  };
  return ticks2.reduce((childProps, tick, index) => {
    childProps[index] = {
      axis: axisProps,
      axisLabel: axisLabelProps,
      ticks: getTickProps2(props, calculatedValues, tick, index),
      tickLabels: getTickLabelProps2(props, calculatedValues, tick, index),
      grid: getGridProps2(props, calculatedValues, tick, index)
    };
    return childProps;
  }, initialChildProps);
};

// node_modules/victory-polar-axis/es/victory-polar-axis.js
var fallbackProps7 = {
  width: 450,
  height: 300,
  padding: 50
};
var VictoryPolarAxisBase = class extends import_react50.default.Component {
  static getScale(props) {
    return getScale4(props);
  }
  static getStyles(props) {
    return getStyles6(props, fallbackProps7.style);
  }
  static getBaseProps(props) {
    return getBaseProps6(props, fallbackProps7);
  }
  renderAxisLine(props) {
    const {
      dependentAxis
    } = props;
    const axisComponent = dependentAxis ? props.axisComponent : props.circularAxisComponent;
    const axisProps = this.getComponentProps(axisComponent, "axis", 0);
    return import_react50.default.cloneElement(axisComponent, axisProps);
  }
  renderLabel(props) {
    const {
      axisLabelComponent,
      dependentAxis,
      label
    } = props;
    if (!label || !dependentAxis) {
      return null;
    }
    const axisLabelProps = this.getComponentProps(axisLabelComponent, "axisLabel", 0);
    return import_react50.default.cloneElement(axisLabelComponent, axisLabelProps);
  }
  renderAxis(props) {
    const {
      tickComponent,
      tickLabelComponent,
      name
    } = props;
    const shouldRender = (componentProps) => {
      const {
        style = {},
        events = {}
      } = componentProps;
      const visible = style.stroke !== "transparent" && style.stroke !== "none" && style.strokeWidth !== 0;
      return visible || !(0, import_isEmpty7.default)(events);
    };
    const axisType = props.dependentAxis ? "radial" : "angular";
    const gridComponent = axisType === "radial" ? props.circularGridComponent : props.gridComponent;
    const tickComponents = this.dataKeys.map((key, index) => {
      const tickProps = Object.assign({
        key: `${name}-tick-${key}`
      }, this.getComponentProps(tickComponent, "ticks", index));
      const TickComponent = import_react50.default.cloneElement(tickComponent, tickProps);
      return shouldRender(TickComponent.props) ? TickComponent : void 0;
    }).filter(Boolean);
    const gridComponents = this.dataKeys.map((key, index) => {
      const gridProps = Object.assign({
        key: `${name}-grid-${key}`
      }, this.getComponentProps(gridComponent, "grid", index));
      const GridComponent = import_react50.default.cloneElement(gridComponent, gridProps);
      return shouldRender(GridComponent.props) ? GridComponent : void 0;
    }).filter(Boolean);
    const tickLabelComponents = this.dataKeys.map((key, index) => {
      const tickLabelProps = Object.assign({
        key: `${name}-tick-${key}`
      }, this.getComponentProps(tickLabelComponent, "tickLabels", index));
      return import_react50.default.cloneElement(tickLabelComponent, tickLabelProps);
    });
    const axis = this.renderAxisLine(props);
    const axisLabel = this.renderLabel(props);
    const children = [axis, axisLabel, ...tickComponents, ...gridComponents, ...tickLabelComponents];
    return this.renderGroup(props, children);
  }
  // Overridden in victory-native
  renderGroup(props, children) {
    const {
      groupComponent
    } = props;
    return import_react50.default.cloneElement(groupComponent, {}, children);
  }
  shouldAnimate() {
    return !!this.props.animate;
  }
  render() {
    const {
      animationWhitelist
    } = VictoryPolarAxis;
    const props = axis_exports.modifyProps(this.props, fallbackProps7);
    if (this.shouldAnimate()) {
      return this.animateComponent(props, animationWhitelist);
    }
    const children = this.renderAxis(props);
    return props.standalone ? this.renderContainer(props.containerComponent, children) : children;
  }
};
__publicField(VictoryPolarAxisBase, "animationWhitelist", ["style", "domain", "range", "tickCount", "tickValues", "padding", "width", "height"]);
__publicField(VictoryPolarAxisBase, "displayName", "VictoryAxis");
__publicField(VictoryPolarAxisBase, "role", "axis");
__publicField(VictoryPolarAxisBase, "defaultTransitions", {
  onExit: {
    duration: 500
  },
  onEnter: {
    duration: 500
  }
});
__publicField(VictoryPolarAxisBase, "defaultProps", {
  axisComponent: import_react50.default.createElement(LineSegment, null),
  axisLabelComponent: import_react50.default.createElement(VictoryLabel, null),
  circularAxisComponent: import_react50.default.createElement(Arc, null),
  circularGridComponent: import_react50.default.createElement(Arc, null),
  containerComponent: import_react50.default.createElement(VictoryContainer, null),
  endAngle: 360,
  gridComponent: import_react50.default.createElement(LineSegment, null),
  groupComponent: import_react50.default.createElement("g", {
    role: "presentation"
  }),
  labelPlacement: "parallel",
  startAngle: 0,
  standalone: true,
  theme: VictoryTheme.grayscale,
  tickComponent: import_react50.default.createElement(LineSegment, null),
  tickLabelComponent: import_react50.default.createElement(VictoryLabel, null)
});
__publicField(VictoryPolarAxisBase, "getDomain", axis_exports.getDomain);
__publicField(VictoryPolarAxisBase, "getAxis", axis_exports.getAxis);
__publicField(VictoryPolarAxisBase, "expectedComponents", ["axisComponent", "circularAxisComponent", "groupComponent", "containerComponent", "tickComponent", "tickLabelComponent", "gridComponent", "circularGridComponent"]);
var options5 = {
  components: [{
    name: "axis",
    index: 0
  }, {
    name: "axisLabel",
    index: 0
  }, {
    name: "grid"
  }, {
    name: "parent",
    index: "parent"
  }, {
    name: "ticks"
  }, {
    name: "tickLabels"
  }]
};
var VictoryPolarAxis = addEvents(VictoryPolarAxisBase, options5);

// node_modules/victory-chart/es/helper-methods.js
var import_defaults30 = __toESM(require_defaults());
var import_react51 = __toESM(require_react());
var fallbackProps8 = {
  width: 450,
  height: 300,
  padding: 50
};
function getAxisProps3(child, props, calculatedProps) {
  const {
    domain,
    scale,
    stringMap,
    categories,
    horizontal
  } = calculatedProps;
  return {
    stringMap,
    horizontal,
    categories,
    startAngle: props.startAngle,
    endAngle: props.endAngle,
    innerRadius: props.innerRadius,
    domain,
    scale
  };
}
function getBackgroundWithProps(props, calculatedProps) {
  const backgroundElement = props.backgroundComponent;
  const height = props.polar ? calculatedProps.range.y[1] : calculatedProps.range.y[0] - calculatedProps.range.y[1];
  const width = calculatedProps.range.x[1] - calculatedProps.range.x[0];
  const xScale = props.horizontal ? calculatedProps.scale.y.range()[0] : calculatedProps.scale.x.range()[0];
  const yScale = props.horizontal ? calculatedProps.scale.x.range()[1] : calculatedProps.scale.y.range()[1];
  const xCoordinate = props.polar ? calculatedProps.origin.x : xScale;
  const yCoordinate = props.polar ? calculatedProps.origin.y : yScale;
  const parentName = props.name || "chart";
  const backgroundProps = {
    height,
    polar: props.polar,
    scale: calculatedProps.scale,
    style: props.style.background,
    x: xCoordinate,
    y: yCoordinate,
    key: `${parentName}-background`,
    width
  };
  return import_react51.default.cloneElement(backgroundElement, (0, import_defaults30.default)({}, backgroundElement.props, backgroundProps));
}
function getChildProps(child, props, calculatedProps) {
  const axisChild = axis_exports.findAxisComponents([child]);
  if (axisChild.length > 0) {
    return getAxisProps3(axisChild[0], props, calculatedProps);
  }
  const {
    categories,
    domain,
    range: range3,
    scale,
    stringMap,
    horizontal
  } = calculatedProps;
  return {
    categories,
    domain,
    range: range3,
    scale,
    stringMap,
    horizontal
  };
}
function getStyles7(props) {
  const styleProps = props.style && props.style.parent;
  return {
    parent: (0, import_defaults30.default)({}, styleProps, {
      height: "100%",
      width: "100%",
      userSelect: "none"
    })
  };
}
function getCalculatedProps2(initialProps, childComponents) {
  const style = getStyles7(initialProps);
  const props = helpers_exports.modifyProps(initialProps, fallbackProps8, "chart");
  const {
    horizontal,
    polar
  } = props;
  const allStrings = wrapper_exports.getStringsFromChildren(props, childComponents);
  const categories = wrapper_exports.getCategories(props, childComponents, allStrings);
  const stringMap = createStringMap2(props, childComponents, allStrings);
  const domain = {
    x: getDomain6(Object.assign({}, props, {
      categories
    }), "x", childComponents),
    y: getDomain6(Object.assign({}, props, {
      categories
    }), "y", childComponents)
  };
  const range3 = {
    x: helpers_exports.getRange(props, "x"),
    y: helpers_exports.getRange(props, "y")
  };
  const baseScale = {
    x: scale_exports.getScaleFromProps(props, "x") || wrapper_exports.getScale(props, "x"),
    y: scale_exports.getScaleFromProps(props, "y") || wrapper_exports.getScale(props, "y")
  };
  const scale = {
    x: baseScale.x.domain(domain.x).range(horizontal ? range3.y : range3.x),
    y: baseScale.y.domain(domain.y).range(horizontal ? range3.x : range3.y)
  };
  const origin = polar ? helpers_exports.getPolarOrigin(props) : axis_exports.getOrigin(domain);
  const padding2 = helpers_exports.getPadding(props);
  return {
    categories,
    domain,
    range: range3,
    horizontal,
    scale,
    stringMap,
    style,
    origin,
    padding: padding2
  };
}
function getChildren(props, childComponents, calculatedProps) {
  const children = childComponents || getChildComponents(props);
  const newCalculatedProps = calculatedProps || getCalculatedProps2(props, children);
  const baseStyle = newCalculatedProps.style.parent;
  const {
    height,
    polar,
    theme,
    width
  } = props;
  const {
    origin,
    horizontal
  } = newCalculatedProps;
  const parentName = props.name || "chart";
  return children.filter(import_react51.default.isValidElement).map((child, index) => {
    const role = child.type && child.type.role;
    const style = Array.isArray(child.props.style) ? child.props.style : (0, import_defaults30.default)({}, child.props.style, {
      parent: baseStyle
    });
    const childProps = getChildProps(child, props, newCalculatedProps);
    const name = child.props.name || `${parentName}-${role}-${index}`;
    const newProps = (0, import_defaults30.default)({
      horizontal,
      height,
      polar,
      theme,
      width,
      style,
      name,
      origin: polar ? origin : void 0,
      padding: newCalculatedProps.padding,
      key: `${name}-key-${index}`,
      standalone: false
    }, childProps);
    return import_react51.default.cloneElement(child, newProps);
  });
}
var getChildComponents = (props, defaultAxes) => {
  let childComponents = import_react51.default.Children.toArray(props.children);
  if (childComponents.length === 0) {
    childComponents.push(defaultAxes.independent, defaultAxes.dependent);
  } else {
    const axisComponents = {
      dependent: axis_exports.getAxisComponentsWithParent(childComponents, "dependent"),
      independent: axis_exports.getAxisComponentsWithParent(childComponents, "independent")
    };
    if (axisComponents.dependent.length === 0 && axisComponents.independent.length === 0) {
      childComponents = props.prependDefaultAxes ? [defaultAxes.independent, defaultAxes.dependent].concat(childComponents) : childComponents.concat([defaultAxes.independent, defaultAxes.dependent]);
    }
  }
  return childComponents;
};
var getDomain6 = (props, axis, childComponents) => {
  const children = childComponents || import_react51.default.Children.toArray(props.children);
  const domain = wrapper_exports.getDomain(props, axis, children);
  const axisComponent = axis_exports.getAxisComponent(children, axis);
  const invertDomain = axisComponent && axisComponent.props && axisComponent.props.invertAxis;
  return invertDomain ? domain.concat().reverse() : domain;
};
var createStringMap2 = (props, childComponents, allStrings) => {
  const x2 = !allStrings.x || allStrings.x.length === 0 ? null : allStrings.x.reduce((memo, string, index) => {
    memo[string] = index + 1;
    return memo;
  }, {});
  const y2 = !allStrings.y || allStrings.y.length === 0 ? null : allStrings.y.reduce((memo, string, index) => {
    memo[string] = index + 1;
    return memo;
  }, {});
  return {
    x: x2,
    y: y2
  };
};

// node_modules/victory-chart/es/victory-chart.js
var import_react_fast_compare7 = __toESM(require_react_fast_compare());
var fallbackProps9 = {
  width: 450,
  height: 300,
  padding: 50
};
var defaultProps13 = {
  backgroundComponent: import_react52.default.createElement(Background, null),
  containerComponent: import_react52.default.createElement(VictoryContainer, null),
  defaultAxes: {
    independent: import_react52.default.createElement(VictoryAxis, null),
    dependent: import_react52.default.createElement(VictoryAxis, {
      dependentAxis: true
    })
  },
  defaultPolarAxes: {
    independent: import_react52.default.createElement(VictoryPolarAxis, null),
    dependent: import_react52.default.createElement(VictoryPolarAxis, {
      dependentAxis: true
    })
  },
  groupComponent: import_react52.default.createElement("g", null),
  standalone: true,
  theme: VictoryTheme.grayscale
};
var VictoryChartImpl = (initialProps) => {
  const propsWithDefaults = import_react52.default.useMemo(() => (0, import_defaults31.default)({}, initialProps, defaultProps13), [initialProps]);
  const role = "chart";
  const {
    getAnimationProps,
    setAnimationState,
    getProps: getProps2
  } = hooks_exports.useAnimationState();
  const props = getProps2(propsWithDefaults);
  const modifiedProps = helpers_exports.modifyProps(props, fallbackProps9, role);
  const {
    desc,
    eventKey,
    containerComponent,
    standalone,
    groupComponent,
    externalEventMutations,
    width,
    height,
    theme,
    polar,
    name,
    title
  } = modifiedProps;
  const axes = props.polar ? modifiedProps.defaultPolarAxes : modifiedProps.defaultAxes;
  const childComponents = import_react52.default.useMemo(() => getChildComponents(modifiedProps, axes), [modifiedProps, axes]);
  const calculatedProps = import_react52.default.useMemo(() => getCalculatedProps2(modifiedProps, childComponents), [modifiedProps, childComponents]);
  const {
    domain,
    scale,
    style,
    origin,
    horizontal
  } = calculatedProps;
  const newChildren = import_react52.default.useMemo(() => {
    const children = getChildren(props, childComponents, calculatedProps);
    const mappedChildren = children.map((child, index) => {
      const childProps = Object.assign({
        animate: getAnimationProps(props, child, index)
      }, child.props);
      return import_react52.default.cloneElement(child, childProps);
    });
    if (props.style && props.style.background) {
      const backgroundComponent = getBackgroundWithProps(props, calculatedProps);
      mappedChildren.unshift(backgroundComponent);
    }
    return mappedChildren;
  }, [getAnimationProps, childComponents, props, calculatedProps]);
  const containerProps = import_react52.default.useMemo(() => {
    if (standalone) {
      return {
        desc,
        domain,
        width,
        height,
        horizontal,
        name,
        origin: polar ? origin : void 0,
        polar,
        theme,
        title,
        scale,
        standalone,
        style: style.parent
      };
    }
    return {};
  }, [desc, domain, height, horizontal, name, origin, polar, scale, standalone, style, title, theme, width]);
  const container = import_react52.default.useMemo(() => {
    if (standalone) {
      const defaultContainerProps = (0, import_defaults31.default)({}, containerComponent.props, containerProps, user_props_exports.getSafeUserProps(propsWithDefaults));
      return import_react52.default.cloneElement(containerComponent, defaultContainerProps);
    }
    return groupComponent;
  }, [groupComponent, standalone, containerComponent, containerProps, propsWithDefaults]);
  const events = import_react52.default.useMemo(() => {
    return wrapper_exports.getAllEvents(props);
  }, [props]);
  const previousProps = hooks_exports.usePreviousProps(propsWithDefaults);
  import_react52.default.useEffect(() => {
    return () => {
      if (propsWithDefaults.animate) {
        setAnimationState(previousProps, propsWithDefaults);
      }
    };
  }, [setAnimationState, previousProps, propsWithDefaults]);
  if (!(0, import_isEmpty8.default)(events)) {
    return import_react52.default.createElement(VictorySharedEvents, {
      container,
      eventKey,
      events,
      externalEventMutations
    }, newChildren);
  }
  return import_react52.default.cloneElement(container, container.props, newChildren);
};
var VictoryChart = import_react52.default.memo(VictoryChartImpl, import_react_fast_compare7.default);
VictoryChart.displayName = "VictoryChart";
VictoryChart.expectedComponents = ["groupComponent", "containerComponent"];

// node_modules/victory-create-container/es/create-container.js
var import_toPairs = __toESM(require_toPairs());
var import_isEmpty10 = __toESM(require_isEmpty());
var import_groupBy3 = __toESM(require_groupBy());
var import_forOwn = __toESM(require_forOwn());

// node_modules/victory-zoom-container/es/victory-zoom-container.js
var import_defaults33 = __toESM(require_defaults());
var import_react54 = __toESM(require_react());

// node_modules/victory-zoom-container/es/zoom-helpers.js
var import_delay = __toESM(require_delay());
var import_defaults32 = __toESM(require_defaults());
var import_throttle2 = __toESM(require_throttle());
var import_react53 = __toESM(require_react());
var RawZoomHelpers = {
  checkDomainEquality(a, b) {
    const checkDimension = (dim) => {
      const val1 = a && a[dim];
      const val2 = b && b[dim];
      if (!val1 && !val2) {
        return true;
      } else if (!val1 || !val2) {
        return false;
      }
      return Number(val1[0]) === Number(val2[0]) && Number(val1[1]) === Number(val2[1]);
    };
    return checkDimension("x") && checkDimension("y");
  },
  /**
   * Generates a new domain scaled by factor and constrained by the original domain.
   * @param  {[Number, Number]} currentDomain  The domain to be scaled.
   * @param  {Object} evt the event object
   * @param  {Object} props the props of the targeted component
   * @param  {String} axis the desired dimension (either x or y)
   * @return {[Number, Number]}                The scale domain
   */
  // eslint-disable-next-line max-params
  scale(currentDomain, evt, props, axis) {
    const [from, to] = currentDomain;
    const range3 = Math.abs(to - from);
    const minimumZoom = props.minimumZoom && props.minimumZoom[axis];
    const factor = this.getScaleFactor(evt);
    if (minimumZoom && range3 <= minimumZoom && factor < 1) {
      return currentDomain;
    }
    const [fromBound, toBound] = this.getDomain(props)[axis];
    const percent = this.getScalePercent(evt, props, axis);
    const point3 = factor * from + percent * (factor * range3);
    const minDomain = this.getMinimumDomain(point3, props, axis);
    const [newMin, newMax] = this.getScaledDomain(currentDomain, factor, percent);
    const newDomain = [newMin > fromBound && newMin < toBound ? newMin : fromBound, newMax < toBound && newMax > fromBound ? newMax : toBound];
    const domain = Math.abs(minDomain[1] - minDomain[0]) > Math.abs(newDomain[1] - newDomain[0]) ? minDomain : newDomain;
    return collection_exports.containsDates([fromBound, toBound]) ? [new Date(domain[0]), new Date(domain[1])] : domain;
  },
  getScaledDomain(currentDomain, factor, percent) {
    const [from, to] = currentDomain;
    const range3 = Math.abs(to - from);
    const diff = range3 - range3 * factor;
    const newMin = Number(from) + diff * Math.max(percent, 0);
    const newMax = Number(to) - diff * Math.max(1 - percent, 0);
    return [Math.min(newMin, newMax), Math.max(newMin, newMax)];
  },
  getMinimumDomain(point3, props, axis) {
    const {
      minimumZoom
    } = props;
    const originalDomain = this.getDomain(props)[axis];
    const [from, to] = originalDomain;
    const defaultMin = Math.abs(from - to) / 1e3;
    const extent2 = minimumZoom ? minimumZoom[axis] || defaultMin : defaultMin;
    const minExtent = point3 - extent2 / 2;
    const maxExtent = point3 + extent2 / 2;
    return [minExtent > from && minExtent < to ? minExtent : from, maxExtent < to && maxExtent > from ? maxExtent : Number(from) + extent2 / 2];
  },
  zoommingOut(evt) {
    return evt.deltaY > 0;
  },
  getScaleFactor(evt) {
    const sign = this.zoommingOut(evt) ? 1 : -1;
    const delta = Math.min(Math.abs(evt.deltaY / 300), 0.5);
    return Math.abs(1 + sign * delta);
  },
  getScalePercent(evt, props, axis) {
    const originalDomain = this.getDomain(props);
    const [from, to] = originalDomain[axis];
    const position = this.getPosition(evt, props, originalDomain);
    return (position[axis] - from) / Math.abs(to - from);
  },
  getPosition(evt, props, originalDomain) {
    const {
      x: x2,
      y: y2
    } = selection_exports.getSVGEventCoordinates(evt);
    const originalScale = {
      x: props.scale.x.domain(originalDomain.x),
      y: props.scale.y.domain(originalDomain.y)
    };
    return selection_exports.getDataCoordinates(props, originalScale, x2, y2);
  },
  /**
   * Generate a new domain translated by the delta and constrained by the original domain.
   * @param  {[Number, Number]} currentDomain  The domain to be translated.
   * @param  {[Number, Number]} originalDomain The original domain for the data set.
   * @param  {Number}           delta          The delta to translate by
   * @return {[Number, Number]}                The translated domain
   */
  pan(currentDomain, originalDomain, delta) {
    const [fromCurrent, toCurrent] = currentDomain.map((val) => Number(val));
    const [fromOriginal, toOriginal] = originalDomain.map((val) => Number(val));
    const lowerBound = fromCurrent + delta;
    const upperBound = toCurrent + delta;
    let newDomain;
    if (lowerBound > fromOriginal && upperBound < toOriginal) {
      newDomain = [lowerBound, upperBound];
    } else if (lowerBound < fromOriginal) {
      const dx = toCurrent - fromCurrent;
      newDomain = [fromOriginal, fromOriginal + dx];
    } else if (upperBound > toOriginal) {
      const dx = toCurrent - fromCurrent;
      newDomain = [toOriginal - dx, toOriginal];
    } else {
      newDomain = currentDomain;
    }
    return collection_exports.containsDates(currentDomain) || collection_exports.containsDates(originalDomain) ? newDomain.map((val) => new Date(val)) : newDomain;
  },
  getDomainScale(domain, scale, axis) {
    const axisDomain = Array.isArray(domain) ? domain : domain[axis];
    const [from, to] = axisDomain;
    const range3 = scale[axis].range();
    const plottableWidth = Math.abs(range3[0] - range3[1]);
    return plottableWidth / (to - from);
  },
  handleAnimation(ctx) {
    const animationTimer = ctx.context.animationTimer;
    const transitionTimer = ctx.context.transitionTimer;
    transitionTimer.bypassAnimation();
    animationTimer.bypassAnimation();
    const resumeAnimation = () => {
      animationTimer.resumeAnimation();
      transitionTimer.resumeAnimation();
    };
    return (0, import_delay.default)(resumeAnimation, 16);
  },
  getLastDomain(targetProps, originalDomain) {
    const {
      zoomDomain,
      cachedZoomDomain,
      currentDomain,
      domain
    } = targetProps;
    if (zoomDomain && !this.checkDomainEquality(zoomDomain, cachedZoomDomain)) {
      return (0, import_defaults32.default)({}, zoomDomain, domain);
    }
    return (0, import_defaults32.default)({}, currentDomain || zoomDomain || originalDomain, domain);
  },
  getDomain(props) {
    const {
      originalDomain,
      domain,
      children,
      zoomDimension
    } = props;
    const childComponents = import_react53.Children.toArray(children);
    let childrenDomain = {};
    if (childComponents.length) {
      childrenDomain = zoomDimension ? {
        [zoomDimension]: wrapper_exports.getDomainFromChildren(props, zoomDimension, childComponents)
      } : {
        x: wrapper_exports.getDomainFromChildren(props, "x", childComponents),
        y: wrapper_exports.getDomainFromChildren(props, "y", childComponents)
      };
    }
    return (0, import_defaults32.default)({}, childrenDomain, originalDomain, domain);
  },
  onMouseDown(evt, targetProps) {
    evt.preventDefault();
    if (!targetProps.allowPan) {
      return void 0;
    }
    const parentSVG = targetProps.parentSVG || selection_exports.getParentSVG(evt);
    const {
      x: x2,
      y: y2
    } = selection_exports.getSVGEventCoordinates(evt, parentSVG);
    return [{
      target: "parent",
      mutation: () => {
        return {
          startX: x2,
          startY: y2,
          panning: true,
          parentSVG,
          parentControlledProps: ["domain"]
        };
      }
    }];
  },
  onMouseUp(evt, targetProps) {
    if (!targetProps.allowPan) {
      return void 0;
    }
    return [{
      target: "parent",
      mutation: () => {
        return {
          panning: false
        };
      }
    }];
  },
  onMouseLeave(evt, targetProps) {
    if (!targetProps.allowPan) {
      return void 0;
    }
    return [{
      target: "parent",
      mutation: () => {
        return {
          panning: false
        };
      }
    }];
  },
  // eslint-disable-next-line max-params, max-statements
  onMouseMove(evt, targetProps, eventKey, ctx) {
    if (targetProps.panning && targetProps.allowPan) {
      const {
        scale,
        startX,
        startY,
        onZoomDomainChange,
        zoomDomain,
        zoomDimension,
        horizontal
      } = targetProps;
      const parentSVG = targetProps.parentSVG || selection_exports.getParentSVG(evt);
      const {
        x: x2,
        y: y2
      } = selection_exports.getSVGEventCoordinates(evt, parentSVG);
      const originalDomain = this.getDomain(targetProps);
      const lastDomain = this.getLastDomain(targetProps, originalDomain);
      const deltaX = horizontal ? y2 - startY : startX - x2;
      const deltaY = horizontal ? startX - x2 : y2 - startY;
      const dx = deltaX / this.getDomainScale(lastDomain, scale, "x");
      const dy = deltaY / this.getDomainScale(lastDomain, scale, "y");
      const currentDomain = {
        x: zoomDimension === "y" ? originalDomain.x : this.pan(lastDomain.x, originalDomain.x, dx),
        y: zoomDimension === "x" ? originalDomain.y : this.pan(lastDomain.y, originalDomain.y, dy)
      };
      const resumeAnimation = this.handleAnimation(ctx);
      const zoomActive = !this.checkDomainEquality(originalDomain, lastDomain);
      const mutatedProps = {
        parentControlledProps: ["domain"],
        startX: x2,
        startY: y2,
        parentSVG,
        currentDomain,
        originalDomain,
        cachedZoomDomain: zoomDomain,
        zoomActive
      };
      if (helpers_exports.isFunction(onZoomDomainChange)) {
        onZoomDomainChange(currentDomain, (0, import_defaults32.default)({}, mutatedProps, targetProps));
      }
      return [{
        target: "parent",
        callback: resumeAnimation,
        mutation: () => mutatedProps
      }];
    }
    return void 0;
  },
  // eslint-disable-next-line max-params
  onWheel(evt, targetProps, eventKey, ctx) {
    if (!targetProps.allowZoom) {
      return void 0;
    }
    const {
      onZoomDomainChange,
      zoomDimension,
      zoomDomain
    } = targetProps;
    const originalDomain = this.getDomain(targetProps);
    const lastDomain = this.getLastDomain(targetProps, originalDomain);
    const {
      x: x2,
      y: y2
    } = lastDomain;
    const currentDomain = {
      x: zoomDimension === "y" ? lastDomain.x : this.scale(x2, evt, targetProps, "x"),
      y: zoomDimension === "x" ? lastDomain.y : this.scale(y2, evt, targetProps, "y")
    };
    const resumeAnimation = this.handleAnimation(ctx);
    const zoomActive = !this.zoommingOut(evt) || // if zoomming in or
    //   if zoomActive is already set AND user hasn't zoommed out all the way
    targetProps.zoomActive && !this.checkDomainEquality(originalDomain, lastDomain);
    const mutatedProps = {
      currentDomain,
      originalDomain,
      cachedZoomDomain: zoomDomain,
      parentControlledProps: ["domain"],
      panning: false,
      zoomActive
    };
    if (helpers_exports.isFunction(onZoomDomainChange)) {
      onZoomDomainChange(currentDomain, (0, import_defaults32.default)({}, mutatedProps, targetProps));
    }
    return [{
      target: "parent",
      callback: resumeAnimation,
      mutation: () => mutatedProps
    }];
  }
};
var ZoomHelpers = {
  checkDomainEquality: RawZoomHelpers.checkDomainEquality.bind(RawZoomHelpers),
  onMouseDown: RawZoomHelpers.onMouseDown.bind(RawZoomHelpers),
  onMouseUp: RawZoomHelpers.onMouseUp.bind(RawZoomHelpers),
  onMouseLeave: RawZoomHelpers.onMouseLeave.bind(RawZoomHelpers),
  onMouseMove: (0, import_throttle2.default)(
    RawZoomHelpers.onMouseMove.bind(RawZoomHelpers),
    16,
    // eslint-disable-line no-magic-numbers
    {
      leading: true,
      trailing: false
    }
  ),
  onWheel: (0, import_throttle2.default)(
    RawZoomHelpers.onWheel.bind(RawZoomHelpers),
    16,
    // eslint-disable-line no-magic-numbers
    {
      leading: true,
      trailing: false
    }
  )
};

// node_modules/victory-zoom-container/es/victory-zoom-container.js
var DEFAULT_DOWNSAMPLE = 150;
var VICTORY_ZOOM_CONTAINER_DEFAULT_PROPS = {
  clipContainerComponent: import_react54.default.createElement(VictoryClipContainer, null),
  allowPan: true,
  allowZoom: true,
  zoomActive: false
};
var useVictoryZoomContainer = (initialProps) => {
  const props = {
    ...VICTORY_ZOOM_CONTAINER_DEFAULT_PROPS,
    ...initialProps
  };
  const {
    children,
    currentDomain,
    zoomActive,
    allowZoom,
    downsample: downsample2,
    scale,
    clipContainerComponent,
    polar,
    origin,
    horizontal
  } = props;
  const downsampleZoomData = (child, domain) => {
    const getData7 = (childProps) => {
      const {
        data: data2,
        x: x2,
        y: y2
      } = childProps;
      const defaultGetData = child.type && typeof child.type.getData === "function" ? child.type.getData : () => void 0;
      return Array.isArray(data2) && !x2 && !y2 ? data2 : defaultGetData(childProps);
    };
    const data = getData7(child.props);
    if (!downsample2 || !domain || !data) {
      return void 0;
    }
    const maxPoints = downsample2 === true ? DEFAULT_DOWNSAMPLE : downsample2;
    const dimension = props.zoomDimension || "x";
    let startIndex = data.findIndex((d) => d[dimension] >= domain[dimension][0]);
    let endIndex = data.findIndex((d) => d[dimension] > domain[dimension][1]);
    if (startIndex !== 0) {
      startIndex -= 1;
    }
    if (endIndex !== -1) {
      endIndex += 1;
    }
    const visibleData = data.slice(startIndex, endIndex);
    return data_exports.downsample(visibleData, maxPoints, startIndex);
  };
  const modifiedChildren = import_react54.default.Children.toArray(children).map((child) => {
    const role = child.type && child.type.role;
    const isDataComponent2 = data_exports.isDataComponent(child);
    const originalDomain = (0, import_defaults33.default)({}, props.originalDomain, props.domain);
    const zoomDomain = (0, import_defaults33.default)({}, props.zoomDomain, props.domain);
    const cachedZoomDomain = (0, import_defaults33.default)({}, props.cachedZoomDomain, props.domain);
    let domain;
    if (!ZoomHelpers.checkDomainEquality(zoomDomain, cachedZoomDomain)) {
      domain = zoomDomain;
    } else if (allowZoom && !zoomActive) {
      domain = child.props.domain;
    } else {
      domain = (0, import_defaults33.default)({}, currentDomain, originalDomain);
    }
    let newDomain = props.polar ? {
      x: originalDomain.x,
      y: [0, domain.y[1]]
    } : domain;
    if (newDomain && props.zoomDimension) {
      newDomain = {
        ...zoomDomain,
        [props.zoomDimension]: newDomain[props.zoomDimension]
      };
    }
    const childProps = isDataComponent2 && role !== "stack" ? {
      domain: newDomain,
      data: downsampleZoomData(child, newDomain)
    } : {
      domain: newDomain
    };
    const newChild = import_react54.default.cloneElement(child, (0, import_defaults33.default)(childProps, child.props));
    if (data_exports.isDataComponent(newChild)) {
      const rangeX = horizontal ? scale.y.range() : scale.x.range();
      const rangeY = horizontal ? scale.x.range() : scale.y.range();
      const plottableWidth = Math.abs(rangeX[0] - rangeX[1]);
      const plottableHeight = Math.abs(rangeY[0] - rangeY[1]);
      const radius = Math.max(...rangeY);
      const groupComponent = import_react54.default.cloneElement(clipContainerComponent, {
        clipWidth: plottableWidth,
        clipHeight: plottableHeight,
        translateX: Math.min(...rangeX),
        translateY: Math.min(...rangeY),
        polar,
        origin: polar ? origin : void 0,
        radius: polar ? radius : void 0,
        ...clipContainerComponent.props
      });
      return import_react54.default.cloneElement(newChild, {
        groupComponent
      });
    }
    return newChild;
  });
  return {
    props,
    children: modifiedChildren
  };
};
var VictoryZoomContainer = (initialProps) => {
  const {
    props,
    children
  } = useVictoryZoomContainer(initialProps);
  return import_react54.default.createElement(VictoryContainer, props, children);
};
VictoryZoomContainer.role = "container";
VictoryZoomContainer.defaultEvents = (initialProps) => {
  const props = {
    ...VICTORY_ZOOM_CONTAINER_DEFAULT_PROPS,
    ...initialProps
  };
  const createEventHandler = (handler, disabled) => (
    // eslint-disable-next-line max-params
    (event, targetProps, eventKey, context) => disabled || props.disable ? {} : handler(event, {
      ...props,
      ...targetProps
    }, eventKey, context)
  );
  return [{
    target: "parent",
    eventHandlers: {
      onMouseDown: createEventHandler(ZoomHelpers.onMouseDown),
      onTouchStart: createEventHandler(ZoomHelpers.onMouseDown),
      onMouseUp: createEventHandler(ZoomHelpers.onMouseUp),
      onTouchEnd: createEventHandler(ZoomHelpers.onMouseUp),
      onMouseLeave: createEventHandler(ZoomHelpers.onMouseLeave),
      onTouchCancel: createEventHandler(ZoomHelpers.onMouseLeave),
      onMouseMove: createEventHandler(ZoomHelpers.onMouseMove),
      onTouchMove: createEventHandler(ZoomHelpers.onMouseMove),
      onWheel: createEventHandler(ZoomHelpers.onWheel, !props.allowZoom)
    }
  }];
};

// node_modules/victory-selection-container/es/victory-selection-container.js
var import_react56 = __toESM(require_react());

// node_modules/victory-selection-container/es/selection-helpers.js
var import_throttle3 = __toESM(require_throttle());
var import_defaults34 = __toESM(require_defaults());
var import_react55 = __toESM(require_react());
var ON_MOUSE_MOVE_THROTTLE_MS = 16;
var SelectionHelpersClass = class {
  constructor() {
    __publicField(this, "onMouseDown", (evt, targetProps) => {
      evt.preventDefault();
      const {
        activateSelectedData,
        allowSelection,
        polar,
        selectedData
      } = targetProps;
      if (!allowSelection) {
        return {};
      }
      const dimension = this.getDimension(targetProps);
      const parentSVG = targetProps.parentSVG || selection_exports.getParentSVG(evt);
      const {
        x: x2,
        y: y2
      } = selection_exports.getSVGEventCoordinates(evt, parentSVG);
      const x1 = polar || dimension !== "y" ? x2 : selection_exports.getDomainCoordinates(targetProps).x[0];
      const y1 = polar || dimension !== "x" ? y2 : selection_exports.getDomainCoordinates(targetProps).y[0];
      const x22 = polar || dimension !== "y" ? x2 : selection_exports.getDomainCoordinates(targetProps).x[1];
      const y22 = polar || dimension !== "x" ? y2 : selection_exports.getDomainCoordinates(targetProps).y[1];
      const mutatedProps = {
        x1,
        y1,
        select: true,
        x2: x22,
        y2: y22,
        parentSVG
      };
      if (selectedData && helpers_exports.isFunction(targetProps.onSelectionCleared)) {
        targetProps.onSelectionCleared((0, import_defaults34.default)({}, mutatedProps, targetProps));
      }
      const parentMutation = [{
        target: "parent",
        mutation: () => mutatedProps
      }];
      const dataMutation = selectedData && activateSelectedData ? selectedData.map((d) => {
        return {
          childName: d.childName,
          eventKey: d.eventKey,
          target: "data",
          mutation: () => null
        };
      }) : [];
      return parentMutation.concat(...dataMutation);
    });
    __publicField(this, "handleMouseMove", (evt, targetProps) => {
      const {
        allowSelection,
        select,
        polar
      } = targetProps;
      const dimension = this.getDimension(targetProps);
      if (!allowSelection || !select) {
        return null;
      }
      const parentSVG = targetProps.parentSVG || selection_exports.getParentSVG(evt);
      const {
        x: x2,
        y: y2
      } = selection_exports.getSVGEventCoordinates(evt, parentSVG);
      const x22 = polar || dimension !== "y" ? x2 : selection_exports.getDomainCoordinates(targetProps).x[1];
      const y22 = polar || dimension !== "x" ? y2 : selection_exports.getDomainCoordinates(targetProps).y[1];
      return {
        target: "parent",
        mutation: () => {
          return {
            x2: x22,
            y2: y22,
            parentSVG
          };
        }
      };
    });
    __publicField(this, "onMouseMove", (0, import_throttle3.default)(this.handleMouseMove, ON_MOUSE_MOVE_THROTTLE_MS, {
      leading: true,
      trailing: false
    }));
    __publicField(this, "onMouseUp", (evt, targetProps) => {
      const {
        activateSelectedData,
        allowSelection,
        x2,
        y2
      } = targetProps;
      if (!allowSelection) {
        return null;
      }
      if (!x2 || !y2) {
        return [{
          target: "parent",
          mutation: () => {
            return {
              select: false,
              x1: null,
              x2: null,
              y1: null,
              y2: null
            };
          }
        }];
      }
      const datasets = this.getDatasets(targetProps);
      const bounds = selection_exports.getBounds(targetProps);
      const selectedData = this.filterDatasets(targetProps, datasets);
      const mutatedProps = {
        selectedData,
        datasets,
        select: false,
        x1: null,
        x2: null,
        y1: null,
        y2: null
      };
      const callbackMutation = selectedData && helpers_exports.isFunction(targetProps.onSelection) ? targetProps.onSelection(selectedData, bounds, (0, import_defaults34.default)({}, mutatedProps, targetProps)) : {};
      const parentMutation = [{
        target: "parent",
        mutation: () => mutatedProps
      }];
      const dataMutation = selectedData && activateSelectedData ? selectedData.map((d) => {
        return {
          childName: d.childName,
          eventKey: d.eventKey,
          target: "data",
          mutation: () => {
            return Object.assign({
              active: true
            }, callbackMutation);
          }
        };
      }) : [];
      return parentMutation.concat(dataMutation);
    });
  }
  getDimension(props) {
    const {
      horizontal,
      selectionDimension
    } = props;
    if (!horizontal || !selectionDimension) {
      return selectionDimension;
    }
    return selectionDimension === "x" ? "y" : "x";
  }
  getDatasets(props) {
    if (props.data) {
      return [{
        data: props.data
      }];
    }
    const getData7 = (childProps) => {
      const data = data_exports.getData(childProps);
      return Array.isArray(data) && data.length > 0 ? data : void 0;
    };
    const iteratee = (child, childName, parent) => {
      const blacklist = props.selectionBlacklist || [];
      let childElement;
      if (!data_exports.isDataComponent(child) || blacklist.includes(childName)) {
        return null;
      } else if (child.type && helpers_exports.isFunction(child.type.getData)) {
        childElement = parent ? import_react55.default.cloneElement(child, parent.props) : child;
        const childData2 = childElement.props && childElement.type.getData(childElement.props);
        return childData2 ? {
          childName,
          data: childData2
        } : null;
      }
      const childData = getData7(childElement.props);
      return childData ? {
        childName,
        data: childData
      } : null;
    };
    return helpers_exports.reduceChildren(import_react55.default.Children.toArray(props.children), iteratee, props);
  }
  filterDatasets(props, datasets) {
    const filtered = datasets.reduce((memo, dataset) => {
      const selectedData = this.getSelectedData(props, dataset.data);
      return selectedData ? memo.concat({
        childName: dataset.childName,
        eventKey: selectedData.eventKey,
        data: selectedData.data
      }) : memo;
    }, []);
    return filtered.length ? filtered : null;
  }
  getSelectedData(props, dataset) {
    const {
      x1,
      y1,
      x2,
      y2
    } = props;
    const withinBounds = (d) => {
      const scaledPoint = helpers_exports.scalePoint(props, d);
      return scaledPoint.x >= Math.min(x1, x2) && scaledPoint.x <= Math.max(x1, x2) && scaledPoint.y >= Math.min(y1, y2) && scaledPoint.y <= Math.max(y1, y2);
    };
    const eventKey = [];
    const data = [];
    let count = 0;
    for (let index = 0, len = dataset.length; index < len; index++) {
      const datum = dataset[index];
      if (withinBounds(datum)) {
        data[count] = datum;
        eventKey[count] = datum.eventKey === void 0 ? index : datum.eventKey;
        count++;
      }
    }
    return count > 0 ? {
      eventKey,
      data
    } : null;
  }
};
var SelectionHelpers = new SelectionHelpersClass();

// node_modules/victory-selection-container/es/victory-selection-container.js
var VICTORY_SELECTION_CONTAINER_DEFAULT_PROPS = {
  activateSelectedData: true,
  allowSelection: true,
  selectionComponent: import_react56.default.createElement(Rect, null),
  selectionStyle: {
    stroke: "transparent",
    fill: "black",
    fillOpacity: 0.1
  }
};
var useVictorySelectionContainer = (initialProps) => {
  const props = {
    ...VICTORY_SELECTION_CONTAINER_DEFAULT_PROPS,
    ...initialProps
  };
  const {
    x1,
    x2,
    y1,
    y2,
    selectionStyle,
    selectionComponent,
    children,
    name
  } = props;
  const width = Math.abs(x2 - x1) || 1;
  const height = Math.abs(y2 - y1) || 1;
  const x3 = Math.min(x1, x2);
  const y3 = Math.min(y1, y2);
  const shouldRenderRect = y1 && y2 && x1 && x2;
  return {
    props,
    children: [children, shouldRenderRect && import_react56.default.cloneElement(selectionComponent, {
      key: `${name}-selection`,
      x: x3,
      y: y3,
      width,
      height,
      style: selectionStyle
    })]
  };
};
var VictorySelectionContainer = (initialProps) => {
  const {
    props,
    children
  } = useVictorySelectionContainer(initialProps);
  return import_react56.default.createElement(VictoryContainer, props, children);
};
VictorySelectionContainer.role = "container";
VictorySelectionContainer.defaultEvents = (initialProps) => {
  const props = {
    ...VICTORY_SELECTION_CONTAINER_DEFAULT_PROPS,
    ...initialProps
  };
  const createEventHandler = (handler, disabled) => (
    // eslint-disable-next-line max-params
    (event, targetProps, eventKey, context) => disabled || props.disable ? {} : handler(event, {
      ...props,
      ...targetProps
    }, eventKey, context)
  );
  return [{
    target: "parent",
    eventHandlers: {
      onMouseDown: createEventHandler(SelectionHelpers.onMouseDown),
      onTouchStart: createEventHandler(SelectionHelpers.onMouseDown),
      onMouseMove: createEventHandler(SelectionHelpers.onMouseMove),
      onTouchMove: createEventHandler(SelectionHelpers.onMouseMove),
      onMouseUp: createEventHandler(SelectionHelpers.onMouseUp),
      onTouchEnd: createEventHandler(SelectionHelpers.onMouseUp)
    }
  }];
};

// node_modules/victory-create-container/es/create-container.js
var import_react62 = __toESM(require_react());

// node_modules/victory-voronoi-container/es/victory-voronoi-container.js
var import_pick5 = __toESM(require_pick());
var import_defaults37 = __toESM(require_defaults());
var import_react60 = __toESM(require_react());

// node_modules/victory-tooltip/es/victory-tooltip.js
var import_orderBy5 = __toESM(require_orderBy());
var import_isPlainObject8 = __toESM(require_isPlainObject());
var import_uniqueId3 = __toESM(require_uniqueId());
var import_defaults36 = __toESM(require_defaults());
var import_react58 = __toESM(require_react());

// node_modules/victory-tooltip/es/flyout.js
var import_defaults35 = __toESM(require_defaults());
var import_react57 = __toESM(require_react());
var getVerticalPath = (props) => {
  const {
    pointerWidth,
    cornerRadius,
    orientation,
    width,
    height,
    center
  } = props;
  const sign = orientation === "bottom" ? 1 : -1;
  const x2 = props.x + (props.dx || 0);
  const y2 = props.y + (props.dy || 0);
  const centerX = center.x;
  const centerY = center.y;
  const pointerEdge = centerY + sign * (height / 2);
  const oppositeEdge = centerY - sign * (height / 2);
  const rightEdge = centerX + width / 2;
  const leftEdge = centerX - width / 2;
  const pointerLength = sign * (y2 - pointerEdge) < 0 ? 0 : props.pointerLength;
  const direction = orientation === "bottom" ? "0 0 0" : "0 0 1";
  const arc = `${cornerRadius} ${cornerRadius} ${direction}`;
  return `M ${centerX - pointerWidth / 2}, ${pointerEdge}
    L ${pointerLength ? x2 : centerX + pointerWidth / 2}, ${pointerLength ? y2 : pointerEdge}
    L ${centerX + pointerWidth / 2}, ${pointerEdge}
    L ${rightEdge - cornerRadius}, ${pointerEdge}
    A ${arc} ${rightEdge}, ${pointerEdge - sign * cornerRadius}
    L ${rightEdge}, ${oppositeEdge + sign * cornerRadius}
    A ${arc} ${rightEdge - cornerRadius}, ${oppositeEdge}
    L ${leftEdge + cornerRadius}, ${oppositeEdge}
    A ${arc} ${leftEdge}, ${oppositeEdge + sign * cornerRadius}
    L ${leftEdge}, ${pointerEdge - sign * cornerRadius}
    A ${arc} ${leftEdge + cornerRadius}, ${pointerEdge}
    z`;
};
var getHorizontalPath = (props) => {
  const {
    pointerWidth,
    cornerRadius,
    orientation,
    width,
    height,
    center
  } = props;
  const sign = orientation === "left" ? 1 : -1;
  const x2 = props.x + (props.dx || 0);
  const y2 = props.y + (props.dy || 0);
  const centerX = center.x;
  const centerY = center.y;
  const pointerEdge = centerX - sign * (width / 2);
  const oppositeEdge = centerX + sign * (width / 2);
  const bottomEdge = centerY + height / 2;
  const topEdge = centerY - height / 2;
  const pointerLength = sign * (x2 - pointerEdge) > 0 ? 0 : props.pointerLength;
  const direction = orientation === "left" ? "0 0 0" : "0 0 1";
  const arc = `${cornerRadius} ${cornerRadius} ${direction}`;
  return `M ${pointerEdge}, ${centerY - pointerWidth / 2}
    L ${pointerLength ? x2 : pointerEdge}, ${pointerLength ? y2 : centerY + pointerWidth / 2}
    L ${pointerEdge}, ${centerY + pointerWidth / 2}
    L ${pointerEdge}, ${bottomEdge - cornerRadius}
    A ${arc} ${pointerEdge + sign * cornerRadius}, ${bottomEdge}
    L ${oppositeEdge - sign * cornerRadius}, ${bottomEdge}
    A ${arc} ${oppositeEdge}, ${bottomEdge - cornerRadius}
    L ${oppositeEdge}, ${topEdge + cornerRadius}
    A ${arc} ${oppositeEdge - sign * cornerRadius}, ${topEdge}
    L ${pointerEdge + sign * cornerRadius}, ${topEdge}
    A ${arc} ${pointerEdge}, ${topEdge + cornerRadius}
    z`;
};
var getFlyoutPath = (props) => {
  const orientation = props.orientation || "top";
  return orientation === "left" || orientation === "right" ? getHorizontalPath(props) : getVerticalPath(props);
};
var evaluateProps13 = (props) => {
  const id = helpers_exports.evaluateProp(props.id, props);
  const style = helpers_exports.evaluateStyle(props.style, props);
  return {
    ...props,
    id,
    style
  };
};
var defaultProps14 = {
  pathComponent: import_react57.default.createElement(Path, null),
  role: "presentation",
  shapeRendering: "auto"
};
var Flyout = (initialProps) => {
  const props = evaluateProps13((0, import_defaults35.default)({}, initialProps, defaultProps14));
  const userProps = user_props_exports.getSafeUserProps(props);
  user_props_exports.assert(props.height, "Flyout props[height] is undefined");
  user_props_exports.assert(props.width, "Flyout props[width] is undefined");
  user_props_exports.assert(props.x, "Flyout props[x] is undefined");
  user_props_exports.assert(props.y, "Flyout props[y] is undefined");
  const flyoutPathProps = {
    center: props.center || {
      x: 0,
      y: 0
    },
    cornerRadius: props.cornerRadius || 0,
    dx: props.dx,
    dy: props.dy,
    height: props.height,
    orientation: props.orientation || "top",
    pointerLength: props.pointerLength || 0,
    pointerWidth: props.pointerWidth || 0,
    width: props.width,
    x: props.x,
    y: props.y
  };
  return import_react57.default.cloneElement(props.pathComponent, {
    ...props.events,
    ...userProps,
    style: props.style,
    d: getFlyoutPath(flyoutPathProps),
    className: props.className,
    shapeRendering: props.shapeRendering,
    role: props.role,
    transform: props.transform,
    clipPath: props.clipPath
  });
};

// node_modules/victory-tooltip/es/victory-tooltip.js
var fallbackProps10 = {
  cornerRadius: 5,
  pointerLength: 10,
  pointerWidth: 10
};
var VictoryTooltip = class extends import_react58.default.Component {
  static defaultEvents(props) {
    const activate = props.activateData ? [{
      target: "labels",
      mutation: () => ({
        active: true
      })
    }, {
      target: "data",
      mutation: () => ({
        active: true
      })
    }] : [{
      target: "labels",
      mutation: () => ({
        active: true
      })
    }];
    const deactivate = props.activateData ? [{
      target: "labels",
      mutation: () => ({
        active: void 0
      })
    }, {
      target: "data",
      mutation: () => ({
        active: void 0
      })
    }] : [{
      target: "labels",
      mutation: () => ({
        active: void 0
      })
    }];
    return [{
      target: "data",
      eventHandlers: {
        onMouseOver: () => activate,
        onFocus: () => activate,
        onTouchStart: () => activate,
        onMouseOut: () => deactivate,
        onBlur: () => deactivate,
        onTouchEnd: () => deactivate
      }
    }];
  }
  constructor(props) {
    super(props);
    this.id = props.id === void 0 ? (0, import_uniqueId3.default)("tooltip-") : props.id;
  }
  getDefaultOrientation(props) {
    const {
      datum,
      horizontal,
      polar
    } = props;
    if (!polar) {
      const positive = horizontal ? "right" : "top";
      const negative = horizontal ? "left" : "bottom";
      return datum && datum.y < 0 ? negative : positive;
    }
    return this.getPolarOrientation(props);
  }
  getPolarOrientation(props) {
    const degrees = label_helpers_exports.getDegrees(props, props.datum);
    const placement = props.labelPlacement || "vertical";
    if (placement === "vertical") {
      return this.getVerticalOrientations(degrees);
    } else if (placement === "parallel") {
      return degrees < 90 || degrees > 270 ? "right" : "left";
    }
    return degrees > 180 ? "bottom" : "top";
  }
  getVerticalOrientations(degrees) {
    if (degrees < 45 || degrees > 315) {
      return "right";
    } else if (degrees >= 45 && degrees <= 135) {
      return "top";
    } else if (degrees > 135 && degrees < 225) {
      return "left";
    }
    return "bottom";
  }
  getStyles(props) {
    const theme = props.theme || VictoryTheme.grayscale;
    const defaultLabelStyles = theme && theme.tooltip && theme.tooltip.style ? theme.tooltip.style : {};
    const baseLabelStyle = Array.isArray(props.style) ? props.style.map((s) => (0, import_defaults36.default)({}, s, defaultLabelStyles)) : (0, import_defaults36.default)({}, props.style, defaultLabelStyles);
    const defaultFlyoutStyles = theme && theme.tooltip && theme.tooltip.flyoutStyle ? theme.tooltip.flyoutStyle : {};
    const baseFlyoutStyle = props.flyoutStyle ? (0, import_defaults36.default)({}, props.flyoutStyle, defaultFlyoutStyles) : defaultFlyoutStyles;
    const style = Array.isArray(baseLabelStyle) ? baseLabelStyle.map((s) => helpers_exports.evaluateStyle(s, props)) : helpers_exports.evaluateStyle(baseLabelStyle, props);
    const flyoutStyle = helpers_exports.evaluateStyle(baseFlyoutStyle, Object.assign({}, props, {
      style
    }));
    return {
      style,
      flyoutStyle
    };
  }
  getEvaluatedProps(props) {
    const {
      cornerRadius,
      centerOffset,
      dx,
      dy
    } = props;
    const active = helpers_exports.evaluateProp(props.active, props);
    let text = helpers_exports.evaluateProp(props.text, Object.assign({}, props, {
      active
    }));
    if (text === void 0 || text === null) {
      text = "";
    }
    if (typeof text === "number") {
      text = text.toString();
    }
    const {
      style,
      flyoutStyle
    } = this.getStyles(Object.assign({}, props, {
      active,
      text
    }));
    const orientation = helpers_exports.evaluateProp(props.orientation, Object.assign({}, props, {
      active,
      text,
      style,
      flyoutStyle
    })) || this.getDefaultOrientation(props);
    const padding2 = helpers_exports.evaluateProp(props.flyoutPadding, Object.assign({}, props, {
      active,
      text,
      style,
      flyoutStyle,
      orientation
    })) || this.getLabelPadding(style);
    const flyoutPadding = helpers_exports.getPadding({
      padding: padding2
    });
    const pointerWidth = helpers_exports.evaluateProp(props.pointerWidth, Object.assign({}, props, {
      active,
      text,
      style,
      flyoutStyle,
      orientation
    }));
    const pointerLength = helpers_exports.evaluateProp(props.pointerLength, Object.assign({}, props, {
      active,
      text,
      style,
      flyoutStyle,
      orientation
    }));
    const labelSize = textsize_exports.approximateTextSize(text, style);
    const {
      flyoutHeight,
      flyoutWidth
    } = this.getDimensions(Object.assign({}, props, {
      style,
      flyoutStyle,
      active,
      text,
      orientation,
      flyoutPadding,
      pointerWidth,
      pointerLength
    }), labelSize);
    const evaluatedProps = Object.assign({}, props, {
      active,
      text,
      style,
      flyoutStyle,
      orientation,
      flyoutHeight,
      flyoutWidth,
      flyoutPadding,
      pointerWidth,
      pointerLength
    });
    const offsetX = (0, import_isPlainObject8.default)(centerOffset) && (centerOffset == null ? void 0 : centerOffset.x) !== void 0 ? helpers_exports.evaluateProp(centerOffset.x, evaluatedProps) : 0;
    const offsetY = (0, import_isPlainObject8.default)(centerOffset) && (centerOffset == null ? void 0 : centerOffset.y) !== void 0 ? helpers_exports.evaluateProp(centerOffset.y, evaluatedProps) : 0;
    return {
      ...evaluatedProps,
      centerOffset: {
        x: offsetX,
        y: offsetY
      },
      dx: dx !== void 0 ? helpers_exports.evaluateProp(dx, evaluatedProps) : 0,
      dy: dy !== void 0 ? helpers_exports.evaluateProp(dy, evaluatedProps) : 0,
      cornerRadius: helpers_exports.evaluateProp(cornerRadius, evaluatedProps)
    };
  }
  getCalculatedValues(props) {
    const {
      style,
      text,
      flyoutStyle,
      flyoutHeight,
      flyoutWidth
    } = props;
    const labelSize = textsize_exports.approximateTextSize(text, style);
    const flyoutDimensions = {
      height: flyoutHeight,
      width: flyoutWidth
    };
    const flyoutCenter = this.getFlyoutCenter(props, flyoutDimensions);
    const transform = this.getTransform(props);
    return {
      style,
      flyoutStyle,
      labelSize,
      flyoutDimensions,
      flyoutCenter,
      transform
    };
  }
  getTransform(props) {
    const {
      x: x2,
      y: y2,
      style
    } = props;
    const labelStyle = style || {};
    const angle = labelStyle.angle || props.angle || this.getDefaultAngle(props);
    return angle ? `rotate(${angle} ${x2} ${y2})` : void 0;
  }
  getDefaultAngle(props) {
    const {
      polar,
      labelPlacement,
      orientation,
      datum
    } = props;
    if (!polar || !labelPlacement || labelPlacement === "vertical") {
      return 0;
    }
    const degrees = label_helpers_exports.getDegrees(props, datum);
    const sign = degrees > 90 && degrees < 180 || degrees > 270 ? 1 : -1;
    const labelRotation = labelPlacement === "perpendicular" ? 0 : 90;
    let angle = 0;
    if (degrees === 0 || degrees === 180) {
      angle = orientation === "top" && degrees === 180 ? 270 : 90;
    } else if (degrees > 0 && degrees < 180) {
      angle = 90 - degrees;
    } else if (degrees > 180 && degrees < 360) {
      angle = 270 - degrees;
    }
    return angle + sign * labelRotation;
  }
  constrainTooltip(center, props, dimensions) {
    const {
      x: x2,
      y: y2
    } = center;
    const {
      width,
      height
    } = dimensions;
    const extent2 = {
      x: [0, props.width],
      y: [0, props.height]
    };
    const flyoutExtent = {
      x: [x2 - width / 2, x2 + width / 2],
      y: [y2 - height / 2, y2 + height / 2]
    };
    const adjustments = {
      x: [flyoutExtent.x[0] < extent2.x[0] ? extent2.x[0] - flyoutExtent.x[0] : 0, flyoutExtent.x[1] > extent2.x[1] ? flyoutExtent.x[1] - extent2.x[1] : 0],
      y: [flyoutExtent.y[0] < extent2.y[0] ? extent2.y[0] - flyoutExtent.y[0] : 0, flyoutExtent.y[1] > extent2.y[1] ? flyoutExtent.y[1] - extent2.y[1] : 0]
    };
    return {
      x: Math.round(x2 + adjustments.x[0] - adjustments.x[1]),
      y: Math.round(y2 + adjustments.y[0] - adjustments.y[1])
    };
  }
  // eslint-disable-next-line complexity
  getFlyoutCenter(props, dimensions) {
    const {
      x: x2,
      y: y2,
      dx,
      dy,
      pointerLength,
      orientation,
      constrainToVisibleArea,
      centerOffset
    } = props;
    const {
      height,
      width
    } = dimensions;
    const xSign = orientation === "left" ? -1 : 1;
    const ySign = orientation === "bottom" ? -1 : 1;
    const flyoutCenter = {
      x: orientation === "left" || orientation === "right" ? x2 + xSign * (pointerLength + width / 2 + xSign * dx) : x2 + dx,
      y: orientation === "top" || orientation === "bottom" ? y2 - ySign * (pointerLength + height / 2 - ySign * dy) : y2 + dy
    };
    const center = {
      x: (0, import_isPlainObject8.default)(props.center) && props.center.x !== void 0 ? props.center.x : flyoutCenter.x,
      y: (0, import_isPlainObject8.default)(props.center) && props.center.y !== void 0 ? props.center.y : flyoutCenter.y
    };
    const centerWithOffset = {
      x: center.x + centerOffset.x,
      y: center.y + centerOffset.y
    };
    return constrainToVisibleArea ? this.constrainTooltip(centerWithOffset, props, dimensions) : centerWithOffset;
  }
  getLabelPadding(style) {
    if (!style) {
      return 0;
    }
    const paddings = Array.isArray(style) ? style.map((s) => s.padding) : [style.padding];
    return Math.max(...paddings, 0);
  }
  getDimensions(props, labelSize) {
    const {
      orientation,
      pointerLength,
      pointerWidth,
      flyoutHeight,
      flyoutWidth,
      flyoutPadding
    } = props;
    const cornerRadius = helpers_exports.evaluateProp(props.cornerRadius, props);
    const getHeight = () => {
      const calculatedHeight = labelSize.height + flyoutPadding.top + flyoutPadding.bottom;
      const minHeight = orientation === "top" || orientation === "bottom" ? 2 * cornerRadius : 2 * cornerRadius + pointerWidth;
      return Math.max(minHeight, calculatedHeight);
    };
    const getWidth2 = () => {
      const calculatedWidth = labelSize.width + flyoutPadding.left + flyoutPadding.right;
      const minWidth = orientation === "left" || orientation === "right" ? 2 * cornerRadius + pointerLength : 2 * cornerRadius;
      return Math.max(minWidth, calculatedWidth);
    };
    return {
      flyoutHeight: flyoutHeight ? helpers_exports.evaluateProp(flyoutHeight, props) : getHeight(),
      flyoutWidth: flyoutWidth ? helpers_exports.evaluateProp(flyoutWidth, props) : getWidth2()
    };
  }
  getLabelProps(props, calculatedValues) {
    const {
      flyoutCenter,
      style,
      labelSize,
      dy = 0,
      dx = 0
    } = calculatedValues;
    const {
      text,
      datum,
      activePoints,
      labelComponent,
      index,
      flyoutPadding
    } = props;
    const textAnchor = (Array.isArray(style) && style.length ? style[0].textAnchor : style.textAnchor) || "middle";
    const getLabelX = () => {
      if (!textAnchor || textAnchor === "middle") {
        return flyoutCenter.x;
      }
      const sign = textAnchor === "end" ? -1 : 1;
      return flyoutCenter.x - sign * (labelSize.width / 2);
    };
    return (0, import_defaults36.default)({}, labelComponent.props, {
      key: `${this.id}-label-${index}`,
      text,
      datum,
      activePoints,
      textAnchor,
      dy,
      dx,
      style,
      x: getLabelX() + (flyoutPadding.left - flyoutPadding.right) / 2,
      y: flyoutCenter.y + (flyoutPadding.top - flyoutPadding.bottom) / 2,
      verticalAnchor: "middle",
      angle: style.angle
    });
  }
  getPointerOrientation(point3, center, flyoutDimensions) {
    const edges2 = {
      bottom: center.y + flyoutDimensions.height / 2,
      top: center.y - flyoutDimensions.height / 2,
      left: center.x - flyoutDimensions.width / 2,
      right: center.x + flyoutDimensions.width / 2
    };
    const gaps = [{
      side: "top",
      val: edges2.top > point3.y ? edges2.top - point3.y : -1
    }, {
      side: "bottom",
      val: edges2.bottom < point3.y ? point3.y - edges2.bottom : -1
    }, {
      side: "right",
      val: edges2.right < point3.x ? point3.x - edges2.right : -1
    }, {
      side: "left",
      val: edges2.left > point3.x ? edges2.left - point3.x : -1
    }];
    return (0, import_orderBy5.default)(gaps, "val", "desc")[0].side;
  }
  getFlyoutProps(props, calculatedValues) {
    const {
      flyoutDimensions,
      flyoutStyle,
      flyoutCenter
    } = calculatedValues;
    const {
      x: x2,
      y: y2,
      dx,
      dy,
      datum,
      activePoints,
      index,
      pointerLength,
      pointerWidth,
      cornerRadius,
      events,
      flyoutComponent
    } = props;
    const pointerOrientation = helpers_exports.evaluateProp(props.pointerOrientation, props);
    return (0, import_defaults36.default)({}, flyoutComponent.props, {
      x: x2,
      y: y2,
      dx,
      dy,
      datum,
      activePoints,
      index,
      pointerLength,
      pointerWidth,
      cornerRadius,
      events,
      orientation: pointerOrientation || this.getPointerOrientation({
        x: x2,
        y: y2
      }, flyoutCenter, flyoutDimensions),
      key: `${this.id}-tooltip-${index}`,
      width: flyoutDimensions.width,
      height: flyoutDimensions.height,
      style: flyoutStyle,
      center: flyoutCenter
    });
  }
  // Overridden in victory-core-native
  renderTooltip(props) {
    const active = helpers_exports.evaluateProp(props.active, props);
    const {
      renderInPortal
    } = props;
    if (!active) {
      return null;
    }
    const evaluatedProps = this.getEvaluatedProps(props);
    const {
      flyoutComponent,
      labelComponent,
      groupComponent
    } = evaluatedProps;
    const calculatedValues = this.getCalculatedValues(evaluatedProps);
    const children = [import_react58.default.cloneElement(flyoutComponent, this.getFlyoutProps(evaluatedProps, calculatedValues)), import_react58.default.cloneElement(labelComponent, this.getLabelProps(evaluatedProps, calculatedValues))];
    const tooltip = import_react58.default.cloneElement(groupComponent, {
      role: "presentation",
      transform: calculatedValues.transform
    }, children);
    return renderInPortal ? import_react58.default.createElement(VictoryPortal, null, tooltip) : tooltip;
  }
  render() {
    const props = helpers_exports.modifyProps(this.props, fallbackProps10, "tooltip");
    return this.renderTooltip(props);
  }
};
__publicField(VictoryTooltip, "displayName", "VictoryTooltip");
__publicField(VictoryTooltip, "role", "tooltip");
__publicField(VictoryTooltip, "defaultProps", {
  active: false,
  renderInPortal: true,
  labelComponent: import_react58.default.createElement(VictoryLabel, null),
  flyoutComponent: import_react58.default.createElement(Flyout, null),
  groupComponent: import_react58.default.createElement("g", null)
});

// node_modules/victory-voronoi-container/es/voronoi-helpers.js
var import_throttle4 = __toESM(require_throttle());
var import_isRegExp = __toESM(require_isRegExp());
var import_isEmpty9 = __toESM(require_isEmpty());
var import_react_fast_compare8 = __toESM(require_react_fast_compare());
var import_lib = __toESM(require_lib());
var import_react59 = __toESM(require_react());
var ON_MOUSE_MOVE_THROTTLE_MS2 = 32;
var VoronoiHelpersClass = class {
  constructor() {
    __publicField(this, "onMouseLeave", (evt, targetProps) => {
      const activePoints = targetProps.activePoints || [];
      this.onDeactivated(targetProps, activePoints);
      const inactiveMutations = activePoints.length ? activePoints.map((point3) => this.getInactiveMutations(targetProps, point3)) : [];
      return this.getParentMutation([]).concat(...inactiveMutations);
    });
    __publicField(this, "handleMouseMove", (evt, targetProps) => {
      const activePoints = targetProps.activePoints || [];
      const parentSVG = targetProps.parentSVG || selection_exports.getParentSVG(evt);
      const mousePosition = selection_exports.getSVGEventCoordinates(evt, parentSVG);
      if (!this.withinBounds(targetProps, mousePosition)) {
        this.onDeactivated(targetProps, activePoints);
        const inactiveMutations2 = activePoints.length ? activePoints.map((point3) => this.getInactiveMutations(targetProps, point3)) : [];
        return this.getParentMutation([], mousePosition, parentSVG).concat(...inactiveMutations2);
      }
      const {
        points = [],
        index
      } = this.getVoronoiPoints(targetProps, mousePosition);
      const parentMutations = this.getParentMutation(points, mousePosition, parentSVG, index);
      if (activePoints.length && (0, import_react_fast_compare8.default)(points, activePoints)) {
        return parentMutations;
      }
      this.onActivated(targetProps, points);
      this.onDeactivated(targetProps, activePoints);
      const activeMutations = points.length ? points.map((point3) => this.getActiveMutations(targetProps, point3)) : [];
      const inactiveMutations = activePoints.length ? activePoints.map((point3) => this.getInactiveMutations(targetProps, point3)) : [];
      return parentMutations.concat(...inactiveMutations, ...activeMutations);
    });
    __publicField(this, "onMouseMove", (0, import_throttle4.default)(this.handleMouseMove, ON_MOUSE_MOVE_THROTTLE_MS2, {
      leading: true,
      trailing: false
    }));
  }
  withinBounds(props, point3) {
    const {
      width,
      height,
      polar,
      origin,
      scale
    } = props;
    const padding2 = helpers_exports.getPadding(props, "voronoiPadding");
    const {
      x: x2,
      y: y2
    } = point3;
    if (polar) {
      const distanceSquared = Math.pow(x2 - origin.x, 2) + Math.pow(y2 - origin.y, 2);
      const radius = Math.max(...scale.y.range());
      return distanceSquared < Math.pow(radius, 2);
    }
    return x2 >= padding2.left && x2 <= width - padding2.right && y2 >= padding2.top && y2 <= height - padding2.bottom;
  }
  getDatasets(props) {
    const minDomain = {
      x: collection_exports.getMinValue(props.domain.x),
      y: collection_exports.getMinValue(props.domain.y)
    };
    const children = import_react59.default.Children.toArray(props.children);
    const addMeta = (data, name, child) => {
      const continuous2 = child && child.type && child.type.continuous;
      const style = child ? child.props && child.props.style : props.style;
      return data.map((datum, index) => {
        const {
          x: x2,
          y: y2,
          y0,
          x0
        } = helpers_exports.getPoint(datum);
        const voronoiX = (Number(x2) + Number(x0)) / 2;
        const voronoiY = (Number(y2) + Number(y0)) / 2;
        return Object.assign({
          _voronoiX: props.voronoiDimension === "y" ? minDomain.x : voronoiX,
          _voronoiY: props.voronoiDimension === "x" ? minDomain.y : voronoiY,
          eventKey: index,
          childName: name,
          continuous: continuous2,
          style
        }, datum);
      });
    };
    if (props.data) {
      return addMeta(props.data);
    }
    const getData7 = (childProps) => {
      const data = data_exports.getData(childProps);
      return Array.isArray(data) && data.length > 0 ? data : void 0;
    };
    const iteratee = (child, childName) => {
      const childProps = child.props || {};
      const name = childProps.name || childName;
      const blacklist = props.voronoiBlacklist || [];
      const blacklistStr = blacklist.filter((value) => !!value && typeof value.valueOf() === "string");
      const blacklistRegExp = blacklist.filter(import_isRegExp.default);
      const isRegExpMatch = blacklistRegExp.some((regExp) => regExp.test(name));
      if (!data_exports.isDataComponent(child) || blacklistStr.includes(name) || isRegExpMatch) {
        return null;
      }
      const getChildData2 = child.type && helpers_exports.isFunction(child.type.getData) ? child.type.getData : getData7;
      const childData = getChildData2(child.props);
      return childData ? addMeta(childData, name, child) : null;
    };
    return helpers_exports.reduceChildren(children, iteratee, props);
  }
  findPoints(datasets, point3) {
    return datasets.filter((d) => {
      return point3._voronoiX === d._voronoiX && point3._voronoiY === d._voronoiY;
    });
  }
  withinRadius(point3, mousePosition, radius) {
    if (!point3) {
      return false;
    }
    if (!radius) {
      return true;
    }
    const {
      x: x2,
      y: y2
    } = mousePosition;
    const distanceSquared = Math.pow(x2 - point3[0], 2) + Math.pow(y2 - point3[1], 2);
    return distanceSquared < Math.pow(radius, 2);
  }
  getVoronoiPoints(props, mousePosition) {
    const datasets = this.getDatasets(props);
    const scaledData = datasets.map((d) => {
      const {
        x: x2,
        y: y2
      } = helpers_exports.scalePoint(props, d);
      return [x2, y2];
    });
    const delaunay = import_lib.default.from(scaledData);
    const index = delaunay.find(mousePosition.x, mousePosition.y);
    const withinRadius = this.withinRadius(scaledData[index], mousePosition, props.radius);
    const points = withinRadius ? this.findPoints(datasets, datasets[index]) : [];
    return {
      points,
      index
    };
  }
  getActiveMutations(props, point3) {
    const {
      childName,
      continuous: continuous2
    } = point3;
    const {
      activateData,
      activateLabels,
      labels
    } = props;
    if (!activateData && !activateLabels) {
      return [];
    }
    const defaultTarget = activateData ? ["data"] : [];
    const targets = labels && !activateLabels ? defaultTarget : defaultTarget.concat("labels");
    if ((0, import_isEmpty9.default)(targets)) {
      return [];
    }
    return targets.map((target) => {
      const eventKey = continuous2 === true && target === "data" ? "all" : point3.eventKey;
      return {
        childName,
        eventKey,
        target,
        mutation: () => ({
          active: true
        })
      };
    });
  }
  getInactiveMutations(props, point3) {
    const {
      childName,
      continuous: continuous2
    } = point3;
    const {
      activateData,
      activateLabels,
      labels
    } = props;
    if (!activateData && !activateLabels) {
      return [];
    }
    const defaultTarget = activateData ? ["data"] : [];
    const targets = labels && !activateLabels ? defaultTarget : defaultTarget.concat("labels");
    if ((0, import_isEmpty9.default)(targets)) {
      return [];
    }
    return targets.map((target) => {
      const eventKey = continuous2 && target === "data" ? "all" : point3.eventKey;
      return {
        childName,
        eventKey,
        target,
        mutation: () => null
      };
    });
  }
  // eslint-disable-next-line max-params
  getParentMutation(activePoints, mousePosition, parentSVG, vIndex) {
    return [{
      target: "parent",
      eventKey: "parent",
      mutation: () => ({
        activePoints,
        mousePosition,
        parentSVG,
        vIndex
      })
    }];
  }
  onActivated(props, points) {
    if (helpers_exports.isFunction(props.onActivated)) {
      props.onActivated(points, props);
    }
  }
  onDeactivated(props, points) {
    if (helpers_exports.isFunction(props.onDeactivated)) {
      props.onDeactivated(points, props);
    }
  }
};
var VoronoiHelpers = new VoronoiHelpersClass();

// node_modules/victory-voronoi-container/es/victory-voronoi-container.js
var VICTORY_VORONOI_CONTAINER_DEFAULT_PROPS = {
  activateData: true,
  activateLabels: true,
  labelComponent: import_react60.default.createElement(VictoryTooltip, null),
  voronoiPadding: 5
};
var getPoint2 = (point3) => {
  const whitelist = ["_x", "_x1", "_x0", "_y", "_y1", "_y0"];
  return (0, import_pick5.default)(point3, whitelist);
};
var useVictoryVoronoiContainer = (initialProps) => {
  const props = {
    ...VICTORY_VORONOI_CONTAINER_DEFAULT_PROPS,
    ...initialProps
  };
  const {
    children
  } = props;
  const getDimension2 = () => {
    const {
      horizontal,
      voronoiDimension
    } = props;
    if (!horizontal || !voronoiDimension) {
      return voronoiDimension;
    }
    return voronoiDimension === "x" ? "y" : "x";
  };
  const getLabelPosition2 = (labelProps, points) => {
    const {
      mousePosition,
      mouseFollowTooltips
    } = props;
    const voronoiDimension = getDimension2();
    const point3 = getPoint2(points[0]);
    const basePosition = helpers_exports.scalePoint(props, point3);
    let center = mouseFollowTooltips ? mousePosition : void 0;
    if (!voronoiDimension || points.length < 2) {
      return {
        ...basePosition,
        center: (0, import_defaults37.default)({}, labelProps.center, center)
      };
    }
    const x2 = voronoiDimension === "y" ? mousePosition.x : basePosition.x;
    const y2 = voronoiDimension === "x" ? mousePosition.y : basePosition.y;
    center = mouseFollowTooltips ? mousePosition : {
      x: x2,
      y: y2
    };
    return {
      x: x2,
      y: y2,
      center: (0, import_defaults37.default)({}, labelProps.center, center)
    };
  };
  const getStyle3 = (points, type) => {
    const {
      labels,
      labelComponent,
      theme
    } = props;
    const componentProps = labelComponent.props || {};
    const themeStyles = theme && theme.voronoi && theme.voronoi.style ? theme.voronoi.style : {};
    const componentStyleArray = type === "flyout" ? componentProps.flyoutStyle : componentProps.style;
    return points.reduce((memo, datum, index) => {
      const labelProps = (0, import_defaults37.default)({}, componentProps, {
        datum,
        active: true
      });
      const text = helpers_exports.isFunction(labels) ? labels(labelProps) : void 0;
      const textArray = text !== void 0 ? `${text}`.split("\n") : [];
      const baseStyle = datum.style && datum.style[type] || {};
      const componentStyle = Array.isArray(componentStyleArray) ? componentStyleArray[index] : componentStyleArray;
      const style = helpers_exports.evaluateStyle((0, import_defaults37.default)({}, componentStyle, baseStyle, themeStyles[type]), labelProps);
      const styleArray = textArray.length ? textArray.map(() => style) : [style];
      return memo.concat(styleArray);
    }, []);
  };
  const getDefaultLabelProps = (points) => {
    const {
      voronoiDimension,
      horizontal,
      mouseFollowTooltips
    } = props;
    const point3 = getPoint2(points[0]);
    const multiPoint = voronoiDimension && points.length > 1;
    const y2 = point3._y1 !== void 0 ? point3._y1 : point3._y;
    const defaultHorizontalOrientation = y2 < 0 ? "left" : "right";
    const defaultOrientation = y2 < 0 ? "bottom" : "top";
    const labelOrientation = horizontal ? defaultHorizontalOrientation : defaultOrientation;
    const orientation = mouseFollowTooltips ? void 0 : labelOrientation;
    return {
      orientation,
      pointerLength: multiPoint ? 0 : void 0,
      constrainToVisibleArea: multiPoint || mouseFollowTooltips ? true : void 0
    };
  };
  const getLabelProps5 = (points) => {
    const {
      labels,
      scale,
      labelComponent,
      theme,
      width,
      height
    } = props;
    const componentProps = labelComponent.props || {};
    const text = points.reduce((memo, datum2) => {
      const labelProps2 = (0, import_defaults37.default)({}, componentProps, {
        datum: datum2,
        active: true
      });
      const t = helpers_exports.isFunction(labels) ? labels(labelProps2) : null;
      if (t === null || t === void 0) {
        return memo;
      }
      return memo.concat(`${t}`.split("\n"));
    }, []);
    const {
      childName,
      eventKey,
      style,
      continuous: continuous2,
      ...datum
    } = points[0];
    const name = props.name === childName ? childName : `${props.name}-${childName}`;
    const labelProps = (0, import_defaults37.default)({
      key: `${name}-${eventKey}-voronoi-tooltip`,
      id: `${name}-${eventKey}-voronoi-tooltip`,
      active: true,
      renderInPortal: false,
      activePoints: points,
      datum,
      scale,
      theme
    }, componentProps, {
      text,
      width,
      height,
      style: getStyle3(points, "labels"),
      flyoutStyle: getStyle3(points, "flyout")[0]
    }, getDefaultLabelProps(points));
    const labelPosition = getLabelPosition2(labelProps, points);
    return (0, import_defaults37.default)({}, labelPosition, labelProps);
  };
  const getTooltip = () => {
    const {
      labels,
      activePoints,
      labelComponent
    } = props;
    if (!labels) {
      return null;
    }
    if (Array.isArray(activePoints) && activePoints.length) {
      const labelProps = getLabelProps5(activePoints);
      const {
        text
      } = labelProps;
      const showLabel = Array.isArray(text) ? text.filter(Boolean).length : text;
      return showLabel ? import_react60.default.cloneElement(labelComponent, labelProps) : null;
    }
    return null;
  };
  return {
    props,
    children: [...import_react60.default.Children.toArray(children), getTooltip()]
  };
};
var VictoryVoronoiContainer = (initialProps) => {
  const {
    props,
    children
  } = useVictoryVoronoiContainer(initialProps);
  return import_react60.default.createElement(VictoryContainer, props, children);
};
VictoryVoronoiContainer.role = "container";
VictoryVoronoiContainer.defaultEvents = (initialProps) => {
  const props = {
    ...VICTORY_VORONOI_CONTAINER_DEFAULT_PROPS,
    ...initialProps
  };
  const createEventHandler = (handler, disabled) => (
    // eslint-disable-next-line max-params
    (event, targetProps, eventKey, context) => disabled || props.disable ? {} : handler(event, {
      ...props,
      ...targetProps
    }, eventKey, context)
  );
  return [{
    target: "parent",
    eventHandlers: {
      onMouseLeave: createEventHandler(VoronoiHelpers.onMouseLeave),
      onTouchCancel: createEventHandler(VoronoiHelpers.onMouseLeave),
      onMouseMove: createEventHandler(VoronoiHelpers.onMouseMove),
      onTouchMove: createEventHandler(VoronoiHelpers.onMouseMove)
    }
  }, {
    target: "data",
    eventHandlers: props.disable ? {} : {
      onMouseOver: () => null,
      onMouseOut: () => null,
      onMouseMove: () => null
    }
  }];
};

// node_modules/victory-cursor-container/es/cursor-helpers.js
var import_throttle5 = __toESM(require_throttle());
var ON_MOUSE_MOVE_THROTTLE_MS3 = 16;
var CursorHelpersClass = class {
  constructor() {
    __publicField(this, "handleMouseMove", (evt, targetProps) => {
      const {
        onCursorChange,
        domain
      } = targetProps;
      const cursorDimension = this.getDimension(targetProps);
      const parentSVG = targetProps.parentSVG || selection_exports.getParentSVG(evt);
      const cursorSVGPosition = selection_exports.getSVGEventCoordinates(evt, parentSVG);
      let cursorValue = selection_exports.getDataCoordinates(targetProps, targetProps.scale, cursorSVGPosition.x, cursorSVGPosition.y);
      const inBounds = this.withinBounds(cursorValue, {
        x1: domain.x[0],
        x2: domain.x[1],
        y1: domain.y[0],
        y2: domain.y[1]
      });
      if (!inBounds) {
        cursorValue = null;
      }
      if (helpers_exports.isFunction(onCursorChange)) {
        if (cursorValue) {
          const value = cursorDimension ? cursorValue[cursorDimension] : cursorValue;
          onCursorChange(value, targetProps);
        } else if (cursorValue !== targetProps.cursorValue) {
          onCursorChange(targetProps.defaultCursorValue || null, targetProps);
        }
      }
      return [{
        target: "parent",
        eventKey: "parent",
        mutation: () => ({
          cursorValue,
          parentSVG
        })
      }];
    });
    __publicField(this, "onMouseMove", (0, import_throttle5.default)(this.handleMouseMove, ON_MOUSE_MOVE_THROTTLE_MS3, {
      leading: true,
      trailing: false
    }));
    __publicField(this, "onMouseLeave", this.handleMouseMove);
    __publicField(this, "onTouchEnd", (evt, targetProps) => {
      const {
        onCursorChange
      } = targetProps;
      if (helpers_exports.isFunction(targetProps.onCursorChange)) {
        onCursorChange(null, targetProps);
      }
      return [{
        target: "parent",
        eventKey: "parent",
        mutation: () => ({
          cursorValue: null
        })
      }];
    });
  }
  getDimension(props) {
    const {
      horizontal,
      cursorDimension
    } = props;
    if (!horizontal || !cursorDimension) {
      return cursorDimension;
    }
    return cursorDimension === "x" ? "y" : "x";
  }
  withinBounds(point3, bounds) {
    const {
      x1,
      x2,
      y1,
      y2
    } = helpers_exports.mapValues(bounds, Number);
    const {
      x: x3,
      y: y3
    } = helpers_exports.mapValues(point3, Number);
    return x3 >= Math.min(x1, x2) && x3 <= Math.max(x1, x2) && y3 >= Math.min(y1, y2) && y3 <= Math.max(y1, y2);
  }
};
var CursorHelpers = new CursorHelpersClass();

// node_modules/victory-cursor-container/es/victory-cursor-container.js
var import_isObject3 = __toESM(require_isObject());
var import_defaults38 = __toESM(require_defaults());
var import_react61 = __toESM(require_react());
var VICTORY_CURSOR_CONTAINER_DEFAULT_PROPS = {
  cursorLabelComponent: import_react61.default.createElement(VictoryLabel, null),
  cursorLabelOffset: {
    x: 5,
    y: -10
  },
  cursorComponent: import_react61.default.createElement(LineSegment, null)
};
var useVictoryCursorContainer = (initialProps) => {
  const props = {
    ...VICTORY_CURSOR_CONTAINER_DEFAULT_PROPS,
    ...initialProps
  };
  const {
    children
  } = props;
  const getCursorPosition = () => {
    const {
      cursorValue,
      defaultCursorValue,
      domain,
      cursorDimension
    } = props;
    if (cursorValue) {
      return cursorValue;
    }
    if (typeof defaultCursorValue === "number") {
      return {
        x: (domain.x[0] + domain.x[1]) / 2,
        y: (domain.y[0] + domain.y[1]) / 2,
        ...cursorDimension ? {
          [cursorDimension]: defaultCursorValue
        } : {}
      };
    }
    return defaultCursorValue;
  };
  const getCursorLabelOffset = () => {
    const {
      cursorLabelOffset
    } = props;
    if (typeof cursorLabelOffset === "number") {
      return {
        x: cursorLabelOffset,
        y: cursorLabelOffset
      };
    }
    return cursorLabelOffset;
  };
  const getPadding3 = () => {
    if (props.padding === void 0) {
      const child = Array.isArray(props.children) ? props.children.find((c) => {
        return (0, import_isObject3.default)(c.props) && c.props.padding !== void 0;
      }) : props.children;
      return helpers_exports.getPadding(child == null ? void 0 : child.props);
    }
    return helpers_exports.getPadding(props);
  };
  const getCursorElements = () => {
    const {
      scale,
      cursorLabelComponent,
      cursorLabel,
      cursorComponent,
      width,
      height,
      name,
      horizontal,
      theme
    } = props;
    const cursorDimension = CursorHelpers.getDimension(props);
    const cursorValue = getCursorPosition();
    const cursorLabelOffset = getCursorLabelOffset();
    if (!cursorValue) {
      return [];
    }
    const newElements = [];
    const padding2 = getPadding3();
    const cursorCoordinates = scale && "x" in scale && "y" in scale && typeof scale.y === "function" && typeof scale.x === "function" ? {
      x: horizontal ? scale.y(cursorValue.y) : scale.x(cursorValue.x),
      y: horizontal ? scale.x(cursorValue.x) : scale.y(cursorValue.y)
    } : {
      x: cursorValue.x,
      y: cursorValue.y
    };
    if (cursorLabel) {
      let labelProps = (0, import_defaults38.default)({
        active: true
      }, cursorLabelComponent.props, {
        x: cursorCoordinates.x + cursorLabelOffset.x,
        y: cursorCoordinates.y + cursorLabelOffset.y,
        datum: cursorValue,
        active: true,
        key: `${name}-cursor-label`
      });
      if (helpers_exports.isTooltip(cursorLabelComponent)) {
        const tooltipTheme = theme && theme.tooltip || {};
        labelProps = (0, import_defaults38.default)({}, labelProps, tooltipTheme);
      }
      newElements.push(import_react61.default.cloneElement(cursorLabelComponent, (0, import_defaults38.default)({}, labelProps, {
        text: helpers_exports.evaluateProp(cursorLabel, labelProps)
      })));
    }
    const cursorStyle = Object.assign({
      stroke: "black"
    }, cursorComponent.props.style);
    if (cursorDimension === "x" || cursorDimension === void 0) {
      newElements.push(import_react61.default.cloneElement(cursorComponent, {
        key: `${name}-x-cursor`,
        x1: cursorCoordinates.x,
        x2: cursorCoordinates.x,
        y1: padding2.top,
        y2: (typeof height === "number" ? height : 0) - padding2.bottom,
        style: cursorStyle
      }));
    }
    if (cursorDimension === "y" || cursorDimension === void 0) {
      newElements.push(import_react61.default.cloneElement(cursorComponent, {
        key: `${name}-y-cursor`,
        x1: padding2.left,
        x2: (typeof width === "number" ? width : 0) - padding2.right,
        y1: cursorCoordinates.y,
        y2: cursorCoordinates.y,
        style: cursorStyle
      }));
    }
    return newElements;
  };
  return {
    props,
    children: [...import_react61.default.Children.toArray(children), ...getCursorElements()]
  };
};
var VictoryCursorContainer = (initialProps) => {
  const {
    props,
    children
  } = useVictoryCursorContainer(initialProps);
  return import_react61.default.createElement(VictoryContainer, props, children);
};
VictoryCursorContainer.role = "container";
VictoryCursorContainer.defaultEvents = (initialProps) => {
  const props = {
    ...VICTORY_CURSOR_CONTAINER_DEFAULT_PROPS,
    ...initialProps
  };
  const createEventHandler = (handler, disabled) => (
    // eslint-disable-next-line max-params
    (event, targetProps, eventKey, context) => disabled || props.disable ? {} : handler(event, {
      ...props,
      ...targetProps
    }, eventKey, context)
  );
  return [{
    target: "parent",
    eventHandlers: {
      onMouseLeave: createEventHandler(CursorHelpers.onMouseLeave),
      onMouseMove: createEventHandler(CursorHelpers.onMouseMove),
      onTouchMove: createEventHandler(CursorHelpers.onMouseMove)
    }
  }];
};

// node_modules/victory-create-container/es/create-container.js
function ensureArray(thing) {
  if (!thing) {
    return [];
  } else if (!Array.isArray(thing)) {
    return [thing];
  }
  return thing;
}
var combineEventHandlers = (eventHandlersArray) => {
  return eventHandlersArray.reduce((localHandlers, finalHandlers) => {
    (0, import_forOwn.default)(localHandlers, (localHandler, eventName) => {
      const existingHandler = finalHandlers[eventName];
      if (existingHandler) {
        finalHandlers[eventName] = function combinedHandler() {
          const existingMutations = ensureArray(existingHandler(...arguments));
          const localMutations = ensureArray(localHandler(...arguments));
          return existingMutations.concat(localMutations);
        };
      } else {
        finalHandlers[eventName] = localHandler;
      }
    });
    return finalHandlers;
  });
};
var combineDefaultEvents = (defaultEvents) => {
  const eventsByTarget = (0, import_groupBy3.default)(defaultEvents, "target");
  const events = (0, import_toPairs.default)(eventsByTarget).map((_ref) => {
    let [target, eventsArray] = _ref;
    const newEventsArray = eventsArray.filter(Boolean);
    return (0, import_isEmpty10.default)(newEventsArray) ? null : {
      target,
      eventHandlers: combineEventHandlers(eventsArray.map((event) => event.eventHandlers))
      // note: does not currently handle eventKey or childName
    };
  });
  return events.filter(Boolean);
};
var CONTAINER_HOOKS = {
  zoom: useVictoryZoomContainer,
  selection: useVictorySelectionContainer,
  brush: useVictoryBrushContainer,
  cursor: useVictoryCursorContainer,
  voronoi: useVictoryVoronoiContainer
};
var CONTAINER_COMPONENTS_WEB = {
  zoom: VictoryZoomContainer,
  selection: VictorySelectionContainer,
  brush: VictoryBrushContainer,
  cursor: VictoryCursorContainer,
  voronoi: VictoryVoronoiContainer
};
function makeCreateContainerFunction(containerComponents, VictoryContainerBase) {
  return function combineContainers(containerA, containerB) {
    const ContainerA = containerComponents[containerA];
    const ContainerB = containerComponents[containerB];
    const useContainerA = CONTAINER_HOOKS[containerA];
    const useContainerB = CONTAINER_HOOKS[containerB];
    const CombinedContainer = (props) => {
      const {
        children: childrenA,
        props: propsA
      } = useContainerA(props);
      const {
        children: combinedChildren,
        props: combinedProps
      } = useContainerB({
        ...propsA,
        children: childrenA
      });
      return import_react62.default.createElement(VictoryContainerBase, combinedProps, combinedChildren);
    };
    CombinedContainer.displayName = `Victory${containerA}${containerB}Container`;
    CombinedContainer.role = "container";
    CombinedContainer.defaultEvents = (props) => combineDefaultEvents([...ContainerA.defaultEvents(props), ...ContainerB.defaultEvents(props)]);
    return CombinedContainer;
  };
}
var createContainer = makeCreateContainerFunction(CONTAINER_COMPONENTS_WEB, VictoryContainer);

// node_modules/victory-errorbar/es/victory-errorbar.js
var import_react64 = __toESM(require_react());

// node_modules/victory-errorbar/es/error-bar.js
var import_defaults39 = __toESM(require_defaults());
var import_react63 = __toESM(require_react());
var renderBorder = (props, error, type) => {
  const vertical = type === "right" || type === "left";
  return import_react63.default.cloneElement(props.lineComponent, {
    ...props.events,
    role: props.role,
    shapeRendering: props.shapeRendering,
    className: props.className,
    style: props.style,
    transform: props.transform,
    key: `${props.id}-border-${type}`,
    x1: vertical ? error[type] : props.x - props.borderWidth,
    x2: vertical ? error[type] : props.x + props.borderWidth,
    y1: vertical ? props.y - props.borderWidth : error[type],
    y2: vertical ? props.y + props.borderWidth : error[type],
    "data-type": `border-${type}`
  });
};
var renderCross = (props, error, type) => {
  const vertical = type === "top" || type === "bottom";
  return import_react63.default.cloneElement(props.lineComponent, {
    ...props.events,
    role: props.role,
    shapeRendering: props.shapeRendering,
    className: props.className,
    style: props.style,
    transform: props.transform,
    key: `${props.id}-cross-${type}`,
    x1: props.x,
    x2: vertical ? props.x : error[type],
    y1: props.y,
    y2: vertical ? error[type] : props.y,
    "data-type": `cross-${type}`
  });
};
var calculateError = (props) => {
  const {
    errorX,
    errorY
  } = props;
  const settings = {
    right: {
      error: errorX,
      errorIndex: 0
    },
    left: {
      error: errorX,
      errorIndex: 1
    },
    top: {
      error: errorY,
      errorIndex: 1
    },
    bottom: {
      error: errorY,
      errorIndex: 0
    }
  };
  const getError = (direction) => {
    const {
      error,
      errorIndex
    } = settings[direction];
    return error ? error[errorIndex] : void 0;
  };
  const result = ["right", "left", "top", "bottom"].reduce((memo, dir) => {
    memo[dir] = getError(dir);
    return memo;
  }, {});
  return result;
};
var evaluateProps14 = (props) => {
  const ariaLabel = helpers_exports.evaluateProp(props.ariaLabel, props);
  const id = helpers_exports.evaluateProp(props.id, props);
  const style = helpers_exports.evaluateStyle(Object.assign({
    stroke: "black"
  }, props.style), props);
  const tabIndex = helpers_exports.evaluateProp(props.tabIndex, props);
  return Object.assign({}, props, {
    ariaLabel,
    id,
    style,
    tabIndex
  });
};
var defaultProps15 = {
  groupComponent: import_react63.default.createElement("g", null),
  lineComponent: import_react63.default.createElement(Line, null),
  role: "presentation",
  shapeRendering: "auto"
};
var ErrorBar = (initialProps) => {
  const props = evaluateProps14((0, import_defaults39.default)({}, initialProps, defaultProps15));
  const {
    groupComponent
  } = props;
  const userProps = user_props_exports.getSafeUserProps(props);
  const {
    tabIndex,
    ariaLabel
  } = props;
  const error = calculateError(props);
  const children = [error.right ? renderBorder(props, error, "right") : null, error.left ? renderBorder(props, error, "left") : null, error.bottom ? renderBorder(props, error, "bottom") : null, error.top ? renderBorder(props, error, "top") : null, error.right ? renderCross(props, error, "right") : null, error.left ? renderCross(props, error, "left") : null, error.bottom ? renderCross(props, error, "bottom") : null, error.top ? renderCross(props, error, "top") : null].filter(Boolean);
  return import_react63.default.cloneElement(groupComponent, {
    tabIndex,
    "aria-label": ariaLabel,
    ...userProps
  }, children);
};

// node_modules/victory-errorbar/es/helper-methods.js
var import_assign = __toESM(require_assign());
var import_defaults40 = __toESM(require_defaults());
var getErrors = (props, datum, axis) => {
  const errorNames = {
    x: "_errorX",
    y: "_errorY"
  };
  const errors = datum[errorNames[axis]];
  if (errors === 0) {
    return false;
  }
  const scale = props.scale[axis];
  return Array.isArray(errors) ? [errors[0] === 0 ? false : scale(errors[0] + datum[`_${axis}`]), errors[1] === 0 ? false : scale(datum[`_${axis}`] - errors[1])] : [scale(errors + datum[`_${axis}`]), scale(datum[`_${axis}`] - errors)];
};
var getData5 = (props) => {
  const accessorTypes = ["x", "y", "errorX", "errorY"];
  if (props.data) {
    return data_exports.formatData(props.data, props, accessorTypes);
  }
  const generatedData = props.errorX || props.errorY ? data_exports.generateData(props) : [];
  return data_exports.formatData(generatedData, props, accessorTypes);
};
var getDomainFromData5 = (props, axis) => {
  const minDomain = domain_exports.getMinFromProps(props, axis);
  const maxDomain = domain_exports.getMaxFromProps(props, axis);
  const dataset = getData5(props);
  if (dataset.length < 1) {
    return minDomain !== void 0 && maxDomain !== void 0 ? domain_exports.getDomainFromMinMax(minDomain, maxDomain) : void 0;
  }
  const error = axis === "x" ? "_errorX" : "_errorY";
  const reduceErrorData = (type) => {
    const baseCondition = type === "min" ? Infinity : -Infinity;
    const errorIndex = type === "min" ? 1 : 0;
    const sign = type === "min" ? -1 : 1;
    return dataset.reduce((memo, datum) => {
      const currentError = Array.isArray(datum[error]) ? datum[error][errorIndex] : datum[error];
      const current = datum[`_${axis}`] + sign * (currentError || 0);
      return memo < current && type === "min" || memo > current && type === "max" ? memo : current;
    }, baseCondition);
  };
  const min2 = minDomain !== void 0 ? minDomain : reduceErrorData("min");
  const max2 = maxDomain !== void 0 ? maxDomain : reduceErrorData("max");
  return domain_exports.getDomainFromMinMax(min2, max2);
};
var getDomain7 = (props, axis) => {
  return domain_exports.createDomainFunction(getDomainFromData5)(props, axis);
};
var formatDataFromDomain3 = (datum, domain) => {
  const minDomainX = collection_exports.getMinValue(domain.x);
  const maxDomainX = collection_exports.getMaxValue(domain.x);
  const minDomainY = collection_exports.getMinValue(domain.y);
  const maxDomainY = collection_exports.getMaxValue(domain.y);
  let {
    _x,
    _y
  } = datum;
  if (_x < minDomainX || _x > maxDomainX || _y < minDomainY || _y > maxDomainY) _x = _y = null;
  return Object.assign({}, datum, {
    _x,
    _y
  });
};
var getCalculatedValues7 = (props) => {
  const defaultStyles2 = helpers_exports.getDefaultStyles(props, "errorbar");
  const style = helpers_exports.getStyles(props.style, defaultStyles2) || {};
  const data = getData5(props);
  const range3 = {
    x: helpers_exports.getRange(props, "x"),
    y: helpers_exports.getRange(props, "y")
  };
  const domain = {
    x: getDomain7(props, "x"),
    y: getDomain7(props, "y")
  };
  const scale = {
    x: scale_exports.getBaseScale(props, "x").domain(domain.x).range(props.horizontal ? range3.y : range3.x),
    y: scale_exports.getBaseScale(props, "y").domain(domain.y).range(props.horizontal ? range3.x : range3.y)
  };
  const origin = props.polar ? props.origin || helpers_exports.getPolarOrigin(props) : void 0;
  return {
    domain,
    data,
    scale,
    style,
    origin
  };
};
var getLabelProps3 = (dataProps, text, style) => {
  const {
    x: x2,
    y: y2,
    index,
    scale,
    errorY,
    errorX,
    horizontal,
    labelComponent,
    theme,
    disableInlineStyles
  } = dataProps;
  const getError = function(type) {
    if (type === void 0) {
      type = "x";
    }
    const baseError = type === "y" ? errorY : errorX;
    const error = baseError && Array.isArray(baseError) ? baseError[0] : baseError;
    return error || dataProps[type];
  };
  const labelStyle = style.labels || {};
  const padding2 = labelStyle.padding || 0;
  const textAnchor = horizontal ? "start" : "middle";
  const verticalAnchor = horizontal ? "middle" : "end";
  const labelProps = {
    style: labelStyle,
    y: horizontal ? y2 : getError("y"),
    x: horizontal ? getError("x") : x2,
    dy: horizontal ? 0 : -padding2,
    dx: horizontal ? padding2 : 0,
    text,
    index,
    scale,
    datum: dataProps.datum,
    data: dataProps.data,
    textAnchor: labelStyle.textAnchor || textAnchor,
    verticalAnchor: labelStyle.verticalAnchor || verticalAnchor,
    angle: labelStyle.angle,
    horizontal,
    disableInlineStyles
  };
  if (!helpers_exports.isTooltip(labelComponent)) {
    return labelProps;
  }
  const tooltipTheme = theme && theme.tooltip || {};
  return (0, import_defaults40.default)({}, labelProps, helpers_exports.omit(tooltipTheme, ["style"]));
};
var getBaseProps7 = (initialProps, fallbackProps22) => {
  const modifiedProps = helpers_exports.modifyProps(initialProps, fallbackProps22, "errorbar");
  const props = Object.assign({}, modifiedProps, getCalculatedValues7(modifiedProps));
  const {
    borderWidth,
    data,
    domain,
    events,
    groupComponent,
    height,
    horizontal,
    labels,
    name,
    origin,
    padding: padding2,
    polar,
    scale,
    sharedEvents,
    standalone,
    style,
    theme,
    width,
    disableInlineStyles
  } = props;
  const initialChildProps = {
    parent: {
      data,
      domain,
      height,
      horizontal,
      name,
      origin,
      padding: padding2,
      polar,
      scale,
      standalone,
      style: style.parent,
      theme,
      width
    }
  };
  return data.reduce((childProps, datum, index) => {
    const eventKey = !helpers_exports.isNil(datum.eventKey) ? datum.eventKey : index;
    const {
      x: x2,
      y: y2
    } = helpers_exports.scalePoint((0, import_assign.default)({}, props, {
      scale
    }), datum);
    const formattedDatum = formatDataFromDomain3(datum, domain);
    const errorX = getErrors(props, formattedDatum, "x");
    const errorY = getErrors(props, formattedDatum, "y");
    const dataProps = {
      borderWidth,
      data,
      datum: formattedDatum,
      errorX: horizontal ? errorY : errorX,
      errorY: horizontal ? errorX : errorY,
      groupComponent,
      horizontal,
      index,
      scale,
      style: disableInlineStyles ? {} : style.data,
      x: x2,
      y: y2,
      disableInlineStyles
    };
    childProps[eventKey] = {
      data: dataProps
    };
    const text = label_helpers_exports.getText(props, datum, index);
    if (text !== void 0 && text !== null || labels && (events || sharedEvents)) {
      childProps[eventKey].labels = getLabelProps3(Object.assign({}, props, dataProps), text, style);
    }
    return childProps;
  }, initialChildProps);
};

// node_modules/victory-errorbar/es/victory-errorbar.js
var fallbackProps11 = {
  width: 450,
  height: 300,
  padding: 50
};
var defaultData4 = [{
  x: 1,
  y: 1,
  errorX: 0.1,
  errorY: 0.1
}, {
  x: 2,
  y: 2,
  errorX: 0.2,
  errorY: 0.2
}, {
  x: 3,
  y: 3,
  errorX: 0.3,
  errorY: 0.3
}, {
  x: 4,
  y: 4,
  errorX: 0.4,
  errorY: 0.4
}];
var VictoryErrorBarBase = class extends import_react64.default.Component {
  static getDomain(props, axis) {
    return getDomain7(props, axis);
  }
  static getData(props) {
    return getData5(props);
  }
  static getBaseProps(props) {
    return getBaseProps7(props, fallbackProps11);
  }
  // Overridden in native versions
  shouldAnimate() {
    return !!this.props.animate;
  }
  render() {
    const {
      animationWhitelist,
      role
    } = VictoryErrorBar;
    const props = helpers_exports.modifyProps(this.props, fallbackProps11, role);
    if (this.shouldAnimate()) {
      return this.animateComponent(props, animationWhitelist);
    }
    const children = this.renderData(props);
    const component = props.standalone ? this.renderContainer(props.containerComponent, children) : children;
    return user_props_exports.withSafeUserProps(component, props);
  }
};
__publicField(VictoryErrorBarBase, "animationWhitelist", ["data", "domain", "height", "padding", "samples", "style", "width", "errorX", "errorY", "borderWidth"]);
__publicField(VictoryErrorBarBase, "displayName", "VictoryErrorBar");
__publicField(VictoryErrorBarBase, "role", "errorbar");
__publicField(VictoryErrorBarBase, "defaultTransitions", default_transitions_exports.discreteTransitions());
__publicField(VictoryErrorBarBase, "defaultProps", {
  containerComponent: import_react64.default.createElement(VictoryContainer, null),
  data: defaultData4,
  dataComponent: import_react64.default.createElement(ErrorBar, null),
  labelComponent: import_react64.default.createElement(VictoryLabel, null),
  groupComponent: import_react64.default.createElement("g", {
    role: "presentation"
  }),
  samples: 50,
  sortOrder: "ascending",
  standalone: true,
  theme: VictoryTheme.grayscale
});
__publicField(VictoryErrorBarBase, "expectedComponents", ["dataComponent", "labelComponent", "groupComponent", "containerComponent"]);
var VictoryErrorBar = addEvents(VictoryErrorBarBase);

// node_modules/victory-group/es/victory-group.js
var import_isEmpty11 = __toESM(require_isEmpty());
var import_defaults41 = __toESM(require_defaults());
var import_react66 = __toESM(require_react());

// node_modules/victory-group/es/helper-methods.js
var import_react65 = __toESM(require_react());
var import_react_fast_compare9 = __toESM(require_react_fast_compare());
var fallbackProps12 = {
  width: 450,
  height: 300,
  padding: 50,
  offset: 0
};
function getCalculatedProps3(initialProps, childComponents) {
  const role = "group";
  const props = helpers_exports.modifyProps(initialProps, fallbackProps12, role);
  const style = wrapper_exports.getStyle(props.theme, props.style, role);
  const {
    offset,
    colorScale,
    color,
    polar,
    horizontal
  } = props;
  const categories = props.categories || wrapper_exports.getCategories(props, childComponents, null);
  const datasets = props.datasets || wrapper_exports.getDataFromChildren(props, null);
  const domain = {
    x: wrapper_exports.getDomain(Object.assign({}, props, {
      categories
    }), "x", childComponents),
    y: wrapper_exports.getDomain(Object.assign({}, props, {
      categories
    }), "y", childComponents)
  };
  const range3 = props.range || {
    x: helpers_exports.getRange(props, "x"),
    y: helpers_exports.getRange(props, "y")
  };
  const baseScale = {
    x: scale_exports.getScaleFromProps(props, "x") || wrapper_exports.getScale(props, "x"),
    y: scale_exports.getScaleFromProps(props, "y") || wrapper_exports.getScale(props, "y")
  };
  const scale = {
    x: baseScale.x.domain(domain.x).range(props.horizontal ? range3.y : range3.x),
    y: baseScale.y.domain(domain.y).range(props.horizontal ? range3.x : range3.y)
  };
  const origin = polar ? props.origin : helpers_exports.getPolarOrigin(props);
  const padding2 = helpers_exports.getPadding(props);
  return {
    datasets,
    categories,
    range: range3,
    domain,
    horizontal,
    scale,
    style,
    colorScale,
    color,
    offset,
    origin,
    padding: padding2
  };
}
var withoutSharedEvents = (props) => {
  const {
    children
  } = props;
  const modifiedChildren = import_react65.default.Children.toArray(children).map((child) => {
    return {
      ...child,
      props: helpers_exports.omit(child.props, ["sharedEvents"])
    };
  });
  props.children = modifiedChildren;
  return props;
};
function useMemoizedProps(initialProps) {
  const modifiedProps = withoutSharedEvents(initialProps);
  const [props, setProps] = import_react65.default.useState(modifiedProps);
  import_react65.default.useEffect(() => {
    if (!(0, import_react_fast_compare9.default)(modifiedProps, props)) {
      setProps(modifiedProps);
    }
  }, [props, setProps, modifiedProps]);
  return import_react65.default.useMemo(() => {
    return getCalculatedProps3(props, props.children);
  }, [props]);
}
function pixelsToValue(props, axis, calculatedProps) {
  if (!props.offset) {
    return 0;
  }
  const currentAxis = helpers_exports.getCurrentAxis(axis, props.horizontal);
  const domain = calculatedProps.domain[axis];
  const range3 = calculatedProps.range[currentAxis];
  const domainExtent = Math.max(...domain) - Math.min(...domain);
  const rangeExtent = Math.max(...range3) - Math.min(...range3);
  return domainExtent / rangeExtent * props.offset;
}
function getX0(props, calculatedProps, index, role) {
  const groupLength = role === "stack" ? calculatedProps.datasets[0].length : calculatedProps.datasets.length;
  const center = (groupLength - 1) / 2;
  const totalWidth = pixelsToValue(props, "x", calculatedProps);
  return (index - center) * totalWidth;
}
function getPolarX0(props, calculatedProps, index, role) {
  const groupLength = role === "stack" ? calculatedProps.datasets[0].length : calculatedProps.datasets.length;
  const center = (groupLength - 1) / 2;
  const width = getAngularWidth2(props, calculatedProps);
  return (index - center) * width;
}
function getAngularWidth2(props, calculatedProps) {
  const {
    range: range3
  } = calculatedProps;
  const angularRange = Math.abs(range3.x[1] - range3.x[0]);
  const r = Math.max(...range3.y);
  return props.offset / (2 * Math.PI * r) * angularRange;
}
function getLabels(props, datasets, index) {
  if (!props.labels) {
    return void 0;
  }
  return Math.floor(datasets.length / 2) === index ? props.labels : void 0;
}
function getChildProps2(props, calculatedProps) {
  const {
    categories,
    domain,
    range: range3,
    scale,
    horizontal,
    origin,
    padding: padding2
  } = calculatedProps;
  const {
    width,
    height,
    theme,
    polar
  } = props;
  return {
    height,
    width,
    theme,
    polar,
    origin,
    categories,
    domain,
    range: range3,
    scale,
    horizontal,
    padding: padding2,
    standalone: false
  };
}
function getColorScale2(props, child) {
  const role = child.type && child.type.role;
  const colorScaleOptions = child.props.colorScale || props.colorScale;
  if (role !== "group" && role !== "stack") {
    return void 0;
  }
  return props.theme && props.theme.group ? colorScaleOptions || props.theme.group.colorScale : colorScaleOptions;
}
function getDataWithOffset(props, defaultDataset, offset) {
  if (defaultDataset === void 0) {
    defaultDataset = [];
  }
  const dataset = props.data || props.y ? data_exports.getData(props) : defaultDataset;
  const xOffset = offset || 0;
  return dataset.map((datum) => {
    const _x1 = datum._x instanceof Date ? new Date(datum._x.getTime() + xOffset) : datum._x + xOffset;
    return Object.assign({}, datum, {
      _x1
    });
  });
}
function getChildren2(initialProps, childComponents, calculatedProps) {
  const props = helpers_exports.modifyProps(initialProps, fallbackProps12, "stack");
  const children = childComponents || import_react65.default.Children.toArray(props.children);
  const newCalculatedProps = calculatedProps || getCalculatedProps3(props, children);
  const {
    datasets
  } = newCalculatedProps;
  const {
    labelComponent,
    polar
  } = props;
  const childProps = getChildProps2(props, newCalculatedProps);
  const parentName = props.name || "group";
  return children.map((child, index) => {
    const role = child.type && child.type.role;
    const xOffset = polar ? getPolarX0(props, newCalculatedProps, index, role) : getX0(props, newCalculatedProps, index, role);
    const style = role === "voronoi" || role === "tooltip" || role === "label" ? child.props.style : wrapper_exports.getChildStyle(child, index, newCalculatedProps);
    const labels = props.labels ? getLabels(props, datasets, index) : child.props.labels;
    const name = child.props.name || `${parentName}-${role}-${index}`;
    return import_react65.default.cloneElement(child, Object.assign({
      labels,
      style,
      key: `${name}-key-${index}`,
      name,
      data: getDataWithOffset(props, datasets[index], xOffset),
      colorScale: getColorScale2(props, child),
      labelComponent: labelComponent || child.props.labelComponent,
      xOffset
    }, childProps));
  });
}

// node_modules/victory-group/es/victory-group.js
var import_react_fast_compare10 = __toESM(require_react_fast_compare());
var fallbackProps13 = {
  width: 450,
  height: 300,
  padding: 50,
  offset: 0
};
var defaultProps16 = {
  containerComponent: import_react66.default.createElement(VictoryContainer, null),
  groupComponent: import_react66.default.createElement("g", null),
  samples: 50,
  standalone: true,
  theme: VictoryTheme.grayscale
};
var VictoryGroupBase = (initialProps) => {
  const role = VictoryGroup == null ? void 0 : VictoryGroup.role;
  const {
    getAnimationProps,
    setAnimationState,
    getProps: getProps2
  } = hooks_exports.useAnimationState();
  const propsWithDefaults = import_react66.default.useMemo(() => (0, import_defaults41.default)({}, initialProps, defaultProps16), [initialProps]);
  const props = getProps2(propsWithDefaults);
  const modifiedProps = helpers_exports.modifyProps(props, fallbackProps13, role);
  const {
    eventKey,
    containerComponent,
    standalone,
    groupComponent,
    externalEventMutations,
    width,
    height,
    theme,
    polar,
    horizontal,
    name
  } = modifiedProps;
  const childComponents = import_react66.default.Children.toArray(modifiedProps.children);
  const calculatedProps = useMemoizedProps(modifiedProps);
  const {
    domain,
    scale,
    style,
    origin
  } = calculatedProps;
  const newChildren = import_react66.default.useMemo(() => {
    const children = getChildren2(props, childComponents, calculatedProps);
    return children.map((child, index) => {
      const childProps = Object.assign({
        animate: getAnimationProps(props, child, index)
      }, child.props);
      return import_react66.default.cloneElement(child, childProps);
    });
  }, [props, childComponents, calculatedProps, getAnimationProps]);
  const containerProps = import_react66.default.useMemo(() => {
    if (standalone) {
      return {
        domain,
        scale,
        width,
        height,
        standalone,
        theme,
        style: style.parent,
        horizontal,
        polar,
        origin,
        name
      };
    }
    return {};
  }, [standalone, domain, scale, width, height, theme, style, horizontal, polar, origin, name]);
  const userProps = import_react66.default.useMemo(() => user_props_exports.getSafeUserProps(propsWithDefaults), [propsWithDefaults]);
  const container = import_react66.default.useMemo(() => {
    if (standalone) {
      const defaultContainerProps = (0, import_defaults41.default)({}, containerComponent.props, containerProps, userProps);
      return import_react66.default.cloneElement(containerComponent, defaultContainerProps);
    }
    return import_react66.default.cloneElement(groupComponent, userProps);
  }, [groupComponent, standalone, containerComponent, containerProps, userProps]);
  const events = import_react66.default.useMemo(() => {
    return wrapper_exports.getAllEvents(props);
  }, [props]);
  const previousProps = hooks_exports.usePreviousProps(propsWithDefaults);
  import_react66.default.useEffect(() => {
    return () => {
      if (propsWithDefaults.animate) {
        setAnimationState(previousProps, props);
      }
    };
  }, [setAnimationState, previousProps, propsWithDefaults, props]);
  if (!(0, import_isEmpty11.default)(events)) {
    return import_react66.default.createElement(VictorySharedEvents, {
      container,
      eventKey,
      events,
      externalEventMutations
    }, newChildren);
  }
  return import_react66.default.cloneElement(container, container.props, newChildren);
};
var componentConfig = {
  role: "group",
  expectedComponents: ["groupComponent", "containerComponent", "labelComponent"],
  getChildren: getChildren2
};
var VictoryGroup = Object.assign(import_react66.default.memo(VictoryGroupBase, import_react_fast_compare10.default), componentConfig);
VictoryGroup.displayName = "VictoryGroup";

// node_modules/victory-histogram/es/victory-histogram.js
var import_react67 = __toESM(require_react());

// node_modules/victory-histogram/es/helper-methods.js
var import_react_fast_compare11 = __toESM(require_react_fast_compare());
var cacheLastValue = (func) => {
  let called = false;
  let lastArgs;
  let lastReturnVal;
  return function() {
    for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
      args[_key] = arguments[_key];
    }
    if (called && (0, import_react_fast_compare11.default)(lastArgs, args)) {
      return lastReturnVal;
    }
    const value = func(...args);
    called = true;
    lastReturnVal = value;
    lastArgs = args;
    return value;
  };
};
var dataOrBinsContainDates = (_ref) => {
  let {
    data,
    bins,
    x: x2
  } = _ref;
  const xAccessor = helpers_exports.createAccessor(x2 || "x");
  const dataIsDates = (data == null ? void 0 : data.some((datum) => xAccessor(datum) instanceof Date)) || false;
  const binsHasDates = Array.isArray(bins) && bins.some((bin2) => bin2 instanceof Date);
  return dataIsDates || binsHasDates;
};
var getBinningFunc = (_ref2) => {
  let {
    data,
    x: x2,
    bins,
    dataOrBinsContainsDates
  } = _ref2;
  const xAccessor = helpers_exports.createAccessor(x2 || "x");
  const bin2 = bin().value(xAccessor);
  const niceScale = (dataOrBinsContainsDates ? time() : linear2()).domain(extent(data, xAccessor)).nice();
  if (Array.isArray(bins)) {
    bin2.domain([bins[0], bins[bins.length - 1]]);
    bin2.thresholds(bins.slice(1, bins.length - 1));
    return bin2;
  }
  if (Number.isInteger(bins)) {
    bin2.domain(niceScale.domain());
    bin2.thresholds(bins);
    return bin2;
  }
  if (dataOrBinsContainsDates) {
    bin2.domain(niceScale.domain());
    bin2.thresholds(niceScale.ticks());
    return bin2;
  }
  bin2.domain(niceScale.domain());
  return bin2;
};
var getFormattedData = cacheLastValue((_ref3) => {
  let {
    data = [],
    x: x2,
    bins
  } = _ref3;
  if ((!data || !data.length) && !Array.isArray(bins)) {
    return [];
  }
  const dataOrBinsContainsDates = dataOrBinsContainDates({
    data,
    bins,
    x: x2
  });
  const binFunc = getBinningFunc({
    data,
    x: x2,
    bins,
    dataOrBinsContainsDates
  });
  const foo = binFunc(data);
  const binnedData = [...foo].filter((_ref4) => {
    let {
      x0,
      x1
    } = _ref4;
    if (x0 instanceof Date && x1 instanceof Date) {
      return new Date(x0).getTime() !== new Date(x1).getTime();
    }
    return x0 !== x1;
  });
  const formattedData = binnedData.map((bin2) => {
    const x0 = dataOrBinsContainsDates ? new Date(bin2.x0) : bin2.x0 || 0;
    const x1 = dataOrBinsContainsDates ? new Date(bin2.x1) : bin2.x1 || 0;
    return {
      x0,
      x1,
      x: dataOrBinsContainsDates ? new Date((x0.getTime() + x1.getTime()) / 2) : (x0 + x1) / 2,
      y: bin2.length,
      binnedData: [...bin2]
    };
  });
  return formattedData;
});
var getData6 = (props) => {
  const {
    bins,
    data,
    x: x2
  } = props;
  const dataIsPreformatted = data == null ? void 0 : data.some((_ref5) => {
    let {
      _y
    } = _ref5;
    return !helpers_exports.isNil(_y);
  });
  const formattedData = dataIsPreformatted ? data : getFormattedData({
    data,
    x: x2,
    bins
  });
  return data_exports.getData({
    ...props,
    data: formattedData,
    x: "x"
  });
};
var getDomain8 = (props, axis) => {
  var _a;
  const data = getData6(props);
  if (!data.length) {
    return [0, 1];
  }
  if (axis === "x") {
    const firstBin = data[0];
    const lastBin = data[data.length - 1];
    return domain_exports.getDomainWithZero({
      ...props,
      data: [{
        x: firstBin.x0
      }, {
        x: lastBin.x1
      }],
      x: "x"
    }, "x");
  }
  return ((_a = props.data) == null ? void 0 : _a.length) ? domain_exports.getDomainWithZero({
    ...props,
    data
  }, "y") : [0, 1];
};
var getCalculatedValues8 = (props) => {
  const defaultStyles2 = helpers_exports.getDefaultStyles(props, "histogram");
  const style = helpers_exports.getStyles(props.style, defaultStyles2);
  const range3 = props.range || {
    x: helpers_exports.getRange(props, "x"),
    y: helpers_exports.getRange(props, "y")
  };
  const domain = {
    x: getDomain8(props, "x"),
    y: getDomain8(props, "y")
  };
  let data = getData6(props);
  data = data_exports.formatDataFromDomain(data, domain, 0);
  const scale = {
    x: scale_exports.getBaseScale(props, "x").domain(domain.x).range(props.horizontal ? range3.y : range3.x),
    y: scale_exports.getBaseScale(props, "y").domain(domain.y).range(props.horizontal ? range3.x : range3.y)
  };
  return {
    style,
    data,
    scale,
    domain
  };
};
var getBaseProps8 = (initialProps, fallbackProps22) => {
  const modifiedProps = helpers_exports.modifyProps(initialProps, fallbackProps22, "histogram");
  const props = Object.assign({}, modifiedProps, getCalculatedValues8(modifiedProps));
  const {
    binSpacing,
    cornerRadius,
    data,
    domain,
    events,
    height,
    horizontal,
    padding: padding2,
    scale,
    sharedEvents,
    standalone,
    style,
    theme,
    width,
    labels,
    name,
    getPath: getPath4,
    disableInlineStyles
  } = props;
  const initialChildProps = {
    parent: {
      horizontal,
      domain,
      scale,
      width,
      height,
      data,
      standalone,
      name,
      theme,
      padding: padding2,
      style: style.parent
    }
  };
  const getDistance = (datum) => {
    const current = scale.x(datum.x0);
    const next = scale.x(datum.x1);
    return Math.abs(next - current);
  };
  const getBarWidth2 = (datum) => {
    if (binSpacing) {
      return getDistance(datum) - binSpacing;
    }
    return getDistance(datum);
  };
  return data.reduce((childProps, datum, index) => {
    const eventKey = !helpers_exports.isNil(datum.eventKey) ? datum.eventKey : index;
    const {
      x: x2,
      y: y2,
      y0,
      x0
    } = getBarPosition(props, datum);
    const barWidth = getBarWidth2(datum);
    const dataProps = {
      alignment: "middle",
      barWidth,
      cornerRadius,
      data,
      datum,
      horizontal,
      index,
      scale,
      style: disableInlineStyles ? {} : style.data,
      width,
      height,
      x: x2,
      y: y2,
      y0,
      x0,
      getPath: getPath4,
      disableInlineStyles
    };
    childProps[eventKey] = {
      data: dataProps
    };
    const text = label_helpers_exports.getText(props, datum, index);
    if (text !== void 0 && text !== null || labels && (events || sharedEvents)) {
      childProps[eventKey].labels = label_helpers_exports.getProps(props, index);
    }
    return childProps;
  }, initialChildProps);
};

// node_modules/victory-histogram/es/victory-histogram.js
var fallbackProps14 = {
  width: 450,
  height: 300,
  padding: 50
};
var defaultData5 = [];
var _VictoryHistogramBase = class _VictoryHistogramBase extends import_react67.default.Component {
  static getFormattedData() {
    return getFormattedData(...arguments);
  }
  static getDomain(props, axis) {
    return getDomain8(props, axis);
  }
  static getData(props) {
    return getData6(props);
  }
  static getBaseProps(props) {
    return getBaseProps8(props, fallbackProps14);
  }
  // Overridden in native versions
  shouldAnimate() {
    return !!this.props.animate;
  }
  render() {
    const {
      animationWhitelist,
      role
    } = _VictoryHistogramBase;
    const props = helpers_exports.modifyProps(this.props, fallbackProps14, role);
    if (this.shouldAnimate()) {
      return this.animateComponent(props, animationWhitelist);
    }
    const children = this.renderData(props);
    const component = props.standalone ? this.renderContainer(props.containerComponent, children) : children;
    return user_props_exports.withSafeUserProps(component, props);
  }
};
__publicField(_VictoryHistogramBase, "animationWhitelist", ["data", "domain", "height", "padding", "style", "width"]);
__publicField(_VictoryHistogramBase, "displayName", "VictoryHistogram");
__publicField(_VictoryHistogramBase, "role", "histogram");
__publicField(_VictoryHistogramBase, "defaultTransitions", {
  onLoad: {
    duration: 2e3,
    before: () => ({
      _y: 0,
      _y1: 0,
      _y0: 0
    }),
    after: (datum) => ({
      _y: datum._y,
      _y1: datum._y1,
      _y0: datum._y0
    })
  },
  onExit: {
    duration: 500,
    before: () => ({
      _y: 0,
      yOffset: 0
    })
  },
  onEnter: {
    duration: 500,
    before: () => ({
      _y: 0,
      _y1: 0,
      _y0: 0
    }),
    after: (datum) => ({
      _y: datum._y,
      _y1: datum._y1,
      _y0: datum._y0
    })
  }
});
__publicField(_VictoryHistogramBase, "defaultProps", {
  containerComponent: import_react67.default.createElement(VictoryContainer, null),
  data: defaultData5,
  dataComponent: import_react67.default.createElement(Bar, null),
  groupComponent: import_react67.default.createElement("g", {
    role: "presentation"
  }),
  labelComponent: import_react67.default.createElement(VictoryLabel, null),
  samples: 50,
  sortOrder: "ascending",
  standalone: true,
  theme: VictoryTheme.grayscale
});
__publicField(_VictoryHistogramBase, "expectedComponents", ["dataComponent", "labelComponent", "groupComponent", "containerComponent"]);
var VictoryHistogramBase = _VictoryHistogramBase;
var VictoryHistogram = addEvents(VictoryHistogramBase);

// node_modules/victory-legend/es/victory-legend.js
var import_react68 = __toESM(require_react());

// node_modules/victory-legend/es/helper-methods.js
var import_range = __toESM(require_range());
var import_groupBy4 = __toESM(require_groupBy());
var import_defaults42 = __toESM(require_defaults());
var getColorScale3 = (props) => {
  const {
    colorScale
  } = props;
  return typeof colorScale === "string" ? style_exports.getColorScale(colorScale) : colorScale || [];
};
var getLabelStyles = (props) => {
  const {
    data,
    style
  } = props;
  return data.map((datum, index) => {
    const baseLabelStyles3 = (0, import_defaults42.default)({}, datum.labels, style.labels);
    return helpers_exports.evaluateStyle(baseLabelStyles3, {
      datum,
      index,
      data
    });
  });
};
var getStyles8 = function(props, styleObject) {
  if (styleObject === void 0) {
    styleObject = {};
  }
  const style = props.style || {};
  const parentStyleProps = {
    height: "100%",
    width: "100%"
  };
  return {
    parent: (0, import_defaults42.default)(style.parent, styleObject.parent, parentStyleProps),
    data: (0, import_defaults42.default)({}, style.data, styleObject.data),
    labels: (0, import_defaults42.default)({}, style.labels, styleObject.labels),
    border: (0, import_defaults42.default)({}, style.border, styleObject.border),
    title: (0, import_defaults42.default)({}, style.title, styleObject.title)
  };
};
var getCalculatedValues9 = (props) => {
  const {
    orientation,
    theme
  } = props;
  const defaultStyles2 = theme && theme.legend && theme.legend.style ? theme.legend.style : {};
  const style = getStyles8(props, defaultStyles2);
  const colorScale = getColorScale3(props);
  const isHorizontal2 = orientation === "horizontal";
  const borderPadding = helpers_exports.getPadding({
    padding: props.borderPadding
  });
  return Object.assign({}, props, {
    style,
    isHorizontal: isHorizontal2,
    colorScale,
    borderPadding
  });
};
var getColumn = (props, index) => {
  const {
    itemsPerRow,
    isHorizontal: isHorizontal2
  } = props;
  if (!itemsPerRow) {
    return isHorizontal2 ? index : 0;
  }
  return isHorizontal2 ? index % itemsPerRow : Math.floor(index / itemsPerRow);
};
var getRow = (props, index) => {
  const {
    itemsPerRow,
    isHorizontal: isHorizontal2
  } = props;
  if (!itemsPerRow) {
    return isHorizontal2 ? 0 : index;
  }
  return isHorizontal2 ? Math.floor(index / itemsPerRow) : index % itemsPerRow;
};
var groupData = (props) => {
  const {
    data
  } = props;
  const style = props.style && props.style.data || {};
  const labelStyles = getLabelStyles(props);
  return data.map((datum, index) => {
    const symbol = datum.symbol || {};
    const {
      fontSize: fontSize3
    } = labelStyles[index];
    const size = symbol.size || style.size || fontSize3 / 2.5;
    const symbolSpacer = props.symbolSpacer || Math.max(size, fontSize3);
    return {
      ...datum,
      size,
      symbolSpacer,
      fontSize: fontSize3,
      textSize: textsize_exports.approximateTextSize(datum.name, labelStyles[index]),
      column: getColumn(props, index),
      row: getRow(props, index)
    };
  });
};
var getColumnWidths = (props, data) => {
  const gutter = props.gutter || {};
  const gutterWidth = typeof gutter === "object" ? (gutter.left || 0) + (gutter.right || 0) : gutter || 0;
  const dataByColumn = (0, import_groupBy4.default)(data, "column");
  const columns = Object.keys(dataByColumn);
  return columns.reduce((memo, curr, index) => {
    const lengths = dataByColumn[curr].map((d) => {
      return d.textSize.width + d.size + d.symbolSpacer + gutterWidth;
    });
    memo[index] = Math.max(...lengths);
    return memo;
  }, []);
};
var getRowHeights = (props, data) => {
  const gutter = props.rowGutter || {};
  const gutterHeight = typeof gutter === "object" ? (gutter.top || 0) + (gutter.bottom || 0) : gutter || 0;
  const dataByRow = (0, import_groupBy4.default)(data, "row");
  return Object.keys(dataByRow).reduce((memo, curr, index) => {
    const rows = dataByRow[curr];
    const lengths = rows.map((d) => {
      return d.textSize.height + d.symbolSpacer + gutterHeight;
    });
    memo[index] = Math.max(...lengths);
    return memo;
  }, []);
};
var getTitleDimensions = (props) => {
  const style = props.style && props.style.title || {};
  const textSize = textsize_exports.approximateTextSize(props.title, style);
  const padding2 = style.padding || 0;
  return {
    height: textSize.height + 2 * padding2 || 0,
    width: textSize.width + 2 * padding2 || 0
  };
};
var getOffset3 = (datum, rowHeights, columnWidths) => {
  const {
    column,
    row
  } = datum;
  return {
    x: (0, import_range.default)(column).reduce((memo, curr) => memo + columnWidths[curr], 0),
    y: (0, import_range.default)(row).reduce((memo, curr) => memo + rowHeights[curr], 0)
  };
};
var getAnchors2 = (titleOrientation, centerTitle) => {
  const standardAnchors = {
    textAnchor: titleOrientation === "right" ? "end" : "start",
    verticalAnchor: titleOrientation === "bottom" ? "end" : "start"
  };
  if (centerTitle) {
    const horizontal = titleOrientation === "top" || titleOrientation === "bottom";
    return {
      textAnchor: horizontal ? "middle" : standardAnchors.textAnchor,
      verticalAnchor: horizontal ? standardAnchors.verticalAnchor : "middle"
    };
  }
  return standardAnchors;
};
var getTitleStyle = (props) => {
  const {
    titleOrientation,
    centerTitle,
    titleComponent
  } = props;
  const baseStyle = props.style && props.style.title || {};
  const componentStyle = titleComponent.props && titleComponent.props.style || {};
  const anchors = getAnchors2(titleOrientation, centerTitle);
  return Array.isArray(componentStyle) ? componentStyle.map((obj) => (0, import_defaults42.default)({}, obj, baseStyle, anchors)) : (0, import_defaults42.default)({}, componentStyle, baseStyle, anchors);
};
var getTitleProps = (props, borderProps) => {
  const {
    title,
    titleOrientation,
    centerTitle,
    borderPadding
  } = props;
  const {
    height,
    width
  } = borderProps;
  const style = getTitleStyle(props);
  const padding2 = Array.isArray(style) ? style[0].padding : style.padding;
  const horizontal = titleOrientation === "top" || titleOrientation === "bottom";
  const xOrientation = titleOrientation === "bottom" ? "bottom" : "top";
  const yOrientation = titleOrientation === "right" ? "right" : "left";
  const standardPadding = {
    x: centerTitle ? width / 2 : borderPadding[xOrientation] + (padding2 || 0),
    y: centerTitle ? height / 2 : borderPadding[yOrientation] + (padding2 || 0)
  };
  const getPadding3 = () => {
    return borderPadding[titleOrientation] + (padding2 || 0);
  };
  const xOffset = horizontal ? standardPadding.x : getPadding3();
  const yOffset = horizontal ? getPadding3() : standardPadding.y;
  return {
    x: titleOrientation === "right" ? props.x + width - xOffset : props.x + xOffset,
    y: titleOrientation === "bottom" ? props.y + height - yOffset : props.y + yOffset,
    style,
    text: title
  };
};
var getBorderProps = (props, contentHeight, contentWidth) => {
  const {
    x: x2,
    y: y2,
    borderPadding,
    style
  } = props;
  const height = (contentHeight || 0) + borderPadding.top + borderPadding.bottom;
  const width = (contentWidth || 0) + borderPadding.left + borderPadding.right;
  return {
    x: x2,
    y: y2,
    height,
    width,
    style: Object.assign({
      fill: "none"
    }, style.border)
  };
};
var getDimensions = (initialProps, fallbackProps22) => {
  const modifiedProps = helpers_exports.modifyProps(initialProps, fallbackProps22, "legend");
  const props = Object.assign({}, modifiedProps, getCalculatedValues9(modifiedProps));
  const {
    title,
    titleOrientation
  } = props;
  const groupedData = groupData(props);
  const columnWidths = getColumnWidths(props, groupedData);
  const rowHeights = getRowHeights(props, groupedData);
  const titleDimensions = title ? getTitleDimensions(props) : {
    height: 0,
    width: 0
  };
  return {
    height: titleOrientation === "left" || titleOrientation === "right" ? Math.max(sum(rowHeights), titleDimensions.height) : sum(rowHeights) + titleDimensions.height,
    width: titleOrientation === "left" || titleOrientation === "right" ? sum(columnWidths) + titleDimensions.width : Math.max(sum(columnWidths), titleDimensions.width)
  };
};
var getBaseProps9 = (initialProps, fallbackProps22) => {
  const modifiedProps = helpers_exports.modifyProps(initialProps, fallbackProps22, "legend");
  const props = Object.assign({}, modifiedProps, getCalculatedValues9(modifiedProps));
  const {
    data,
    standalone,
    theme,
    padding: padding2,
    style,
    colorScale,
    gutter,
    rowGutter,
    borderPadding,
    title,
    titleOrientation,
    name,
    x: x2 = 0,
    y: y2 = 0
  } = props;
  const groupedData = groupData(props);
  const columnWidths = getColumnWidths(props, groupedData);
  const rowHeights = getRowHeights(props, groupedData);
  const labelStyles = getLabelStyles(props);
  const titleDimensions = title ? getTitleDimensions(props) : {
    height: 0,
    width: 0
  };
  const titleOffset = {
    x: titleOrientation === "left" ? titleDimensions.width : 0,
    y: titleOrientation === "top" ? titleDimensions.height : 0
  };
  const gutterOffset = {
    x: gutter && typeof gutter === "object" ? gutter.left || 0 : 0,
    y: rowGutter && typeof rowGutter === "object" ? rowGutter.top || 0 : 0
  };
  const {
    height,
    width
  } = getDimensions(props, fallbackProps22);
  const borderProps = getBorderProps(props, height, width);
  const titleProps = getTitleProps(props, borderProps);
  const initialChildProps = {
    parent: {
      data,
      standalone,
      theme,
      padding: padding2,
      name,
      height: props.height,
      width: props.width,
      style: style.parent
    },
    all: {
      border: borderProps,
      title: titleProps
    }
  };
  return groupedData.reduce((childProps, datum, i) => {
    const color = colorScale[i % colorScale.length];
    const dataStyle = (0, import_defaults42.default)({}, datum.symbol, style.data, {
      fill: color
    });
    const eventKey = !helpers_exports.isNil(datum.eventKey) ? datum.eventKey : i;
    const offset = getOffset3(datum, rowHeights, columnWidths);
    const originY = y2 + borderPadding.top + datum.symbolSpacer;
    const originX = x2 + borderPadding.left + datum.symbolSpacer;
    const dataProps = {
      index: i,
      data,
      datum,
      symbol: dataStyle.type || dataStyle.symbol || "circle",
      size: datum.size,
      style: dataStyle,
      y: originY + offset.y + titleOffset.y + gutterOffset.y,
      x: originX + offset.x + titleOffset.x + gutterOffset.x
    };
    const labelProps = {
      datum,
      data,
      text: datum.name,
      style: labelStyles[i],
      y: dataProps.y,
      x: dataProps.x + datum.symbolSpacer + datum.size / 2
    };
    childProps[eventKey] = {
      data: dataProps,
      labels: labelProps
    };
    return childProps;
  }, initialChildProps);
};
function sum(array) {
  if (array && array.length) {
    let value = 0;
    for (let i = 0; i < array.length; i++) {
      value += array[i];
    }
    return value;
  }
  return 0;
}

// node_modules/victory-legend/es/victory-legend.js
var fallbackProps15 = {
  orientation: "vertical",
  titleOrientation: "top",
  width: 450,
  height: 300,
  x: 0,
  y: 0
};
var defaultLegendData = [{
  name: "Series 1"
}, {
  name: "Series 2"
}];
var VictoryLegendBase = class extends import_react68.default.Component {
  static getBaseProps(props) {
    return getBaseProps9(props, fallbackProps15);
  }
  static getDimensions(props) {
    return getDimensions(props, fallbackProps15);
  }
  renderChildren(props) {
    const {
      dataComponent,
      labelComponent,
      title
    } = props;
    const children = [];
    if (props.borderComponent) {
      const borderProps = this.getComponentProps(props.borderComponent, "border", "all");
      const borderComponent = import_react68.default.cloneElement(props.borderComponent, borderProps);
      children.push(borderComponent);
    }
    if (dataComponent) {
      const dataComponents = this.dataKeys.map((_dataKey, index) => {
        if (_dataKey === "all") {
          return void 0;
        }
        const dataProps = this.getComponentProps(dataComponent, "data", index);
        return import_react68.default.cloneElement(dataComponent, dataProps);
      }).filter((comp) => comp !== void 0);
      children.push(...dataComponents);
    }
    if (title && props.titleComponent) {
      const titleProps = this.getComponentProps(title, "title", "all");
      const titleComponent = import_react68.default.cloneElement(props.titleComponent, titleProps);
      children.push(titleComponent);
    }
    if (labelComponent) {
      const labelComponents = this.dataKeys.map((_dataKey, index) => {
        if (_dataKey === "all") {
          return void 0;
        }
        const labelProps = this.getComponentProps(labelComponent, "labels", index);
        if (labelProps.text !== void 0 && labelProps.text !== null) {
          return import_react68.default.cloneElement(labelComponent, labelProps);
        }
        return void 0;
      }).filter((comp) => comp !== void 0);
      children.push(...labelComponents);
    }
    return children;
  }
  render() {
    const {
      role
    } = this.constructor;
    const props = helpers_exports.modifyProps(this.props, fallbackProps15, role);
    const children = this.renderChildren(props);
    return props.standalone ? this.renderContainer(props.containerComponent, children) : import_react68.default.cloneElement(props.groupComponent, {}, children);
  }
};
__publicField(VictoryLegendBase, "displayName", "VictoryLegend");
__publicField(VictoryLegendBase, "role", "legend");
__publicField(VictoryLegendBase, "defaultProps", {
  borderComponent: import_react68.default.createElement(Border, null),
  data: defaultLegendData,
  containerComponent: import_react68.default.createElement(VictoryContainer, null),
  dataComponent: import_react68.default.createElement(Point, null),
  groupComponent: import_react68.default.createElement("g", null),
  labelComponent: import_react68.default.createElement(VictoryLabel, null),
  standalone: true,
  theme: VictoryTheme.grayscale,
  titleComponent: import_react68.default.createElement(VictoryLabel, null)
});
__publicField(VictoryLegendBase, "expectedComponents", ["borderComponent", "containerComponent", "dataComponent", "groupComponent", "labelComponent", "titleComponent"]);
var VictoryLegend = addEvents(VictoryLegendBase);

// node_modules/victory-line/es/victory-line.js
var import_react70 = __toESM(require_react());

// node_modules/victory-line/es/helper-methods.js
var getCalculatedValues10 = (props) => {
  let data = data_exports.getData(props);
  if (data.length < 2) {
    data = [];
  }
  const range3 = {
    x: helpers_exports.getRange(props, "x"),
    y: helpers_exports.getRange(props, "y")
  };
  const domain = {
    x: domain_exports.getDomain(props, "x"),
    y: domain_exports.getDomain(props, "y")
  };
  const scale = {
    x: scale_exports.getBaseScale(props, "x").domain(domain.x).range(props.horizontal ? range3.y : range3.x),
    y: scale_exports.getBaseScale(props, "y").domain(domain.y).range(props.horizontal ? range3.x : range3.y)
  };
  const origin = props.polar ? props.origin || helpers_exports.getPolarOrigin(props) : void 0;
  const defaultStyles2 = helpers_exports.getDefaultStyles(props, "line");
  const style = helpers_exports.getStyles(props.style, defaultStyles2);
  return {
    domain,
    data,
    scale,
    style,
    origin
  };
};
var getBaseProps10 = (initialProps, fallbackProps22) => {
  const modifiedProps = helpers_exports.modifyProps(initialProps, fallbackProps22, "line");
  const props = Object.assign({}, modifiedProps, getCalculatedValues10(modifiedProps));
  const {
    data,
    domain,
    events,
    groupComponent,
    height,
    horizontal,
    interpolation,
    origin,
    padding: padding2,
    polar,
    scale,
    sharedEvents,
    standalone,
    style,
    theme,
    width,
    labels,
    name,
    disableInlineStyles
  } = props;
  const initialChildProps = {
    parent: {
      style: style.parent,
      scale,
      data,
      height,
      width,
      name,
      domain,
      standalone,
      polar,
      origin,
      padding: padding2,
      horizontal
    },
    all: {
      data: {
        horizontal,
        polar,
        origin,
        scale,
        data,
        interpolation,
        groupComponent,
        style: disableInlineStyles ? {} : style.data,
        theme,
        disableInlineStyles
      }
    }
  };
  return data.reduce((childProps, datum, index) => {
    const text = label_helpers_exports.getText(props, datum, index);
    if (text !== void 0 && text !== null || labels && (events || sharedEvents)) {
      const eventKey = !helpers_exports.isNil(datum.eventKey) ? datum.eventKey : index;
      childProps[eventKey] = {
        labels: label_helpers_exports.getProps(props, index)
      };
    }
    return childProps;
  }, initialChildProps);
};

// node_modules/victory-line/es/curve.js
var import_defaults43 = __toESM(require_defaults());
var import_react69 = __toESM(require_react());
var evaluateProps15 = (props) => {
  const ariaLabel = helpers_exports.evaluateProp(props.ariaLabel, props);
  const id = helpers_exports.evaluateProp(props.id, props);
  const style = helpers_exports.evaluateStyle(Object.assign({
    fill: "none",
    stroke: "black",
    pointerEvents: "stroke"
  }, props.style), props);
  const tabIndex = helpers_exports.evaluateProp(props.tabIndex, props);
  return Object.assign({}, props, {
    ariaLabel,
    id,
    style,
    tabIndex
  });
};
var defaultProps17 = {
  pathComponent: import_react69.default.createElement(Path, null),
  role: "presentation",
  shapeRendering: "auto"
};
var Curve = (initialProps) => {
  const props = evaluateProps15((0, import_defaults43.default)({}, initialProps, defaultProps17));
  const userProps = user_props_exports.getSafeUserProps(props);
  const {
    polar,
    origin
  } = props;
  const lineFunction = line_helpers_exports.getLineFunction(props);
  const defaultTransform = polar && origin ? `translate(${origin.x}, ${origin.y})` : void 0;
  const d = lineFunction(props.data);
  return import_react69.default.cloneElement(props.pathComponent, {
    ...props.events,
    ...userProps,
    "aria-label": props.ariaLabel,
    d,
    style: props.style,
    transform: props.transform || defaultTransform,
    className: props.className,
    role: props.role,
    shapeRendering: props.shapeRendering,
    clipPath: props.clipPath,
    tabIndex: props.tabIndex
  });
};

// node_modules/victory-line/es/victory-line.js
var fallbackProps16 = {
  width: 450,
  height: 300,
  padding: 50,
  interpolation: "linear"
};
var options6 = {
  components: [{
    name: "parent",
    index: "parent"
  }, {
    name: "data",
    index: "all"
  }, {
    name: "labels"
  }]
};
var _VictoryLineBase = class _VictoryLineBase extends import_react70.default.Component {
  constructor(props) {
    super(props);
  }
  static getBaseProps(props) {
    return getBaseProps10(props, fallbackProps16);
  }
  // Overridden in native versions
  shouldAnimate() {
    return !!this.props.animate;
  }
  render() {
    const {
      animationWhitelist,
      role
    } = _VictoryLineBase;
    const props = helpers_exports.modifyProps(this.props, fallbackProps16, role);
    if (this.shouldAnimate()) {
      return this.animateComponent(props, animationWhitelist);
    }
    const children = this.renderContinuousData(props);
    const component = props.standalone ? this.renderContainer(props.containerComponent, children) : children;
    return user_props_exports.withSafeUserProps(component, props);
  }
};
__publicField(_VictoryLineBase, "animationWhitelist", ["data", "domain", "height", "padding", "samples", "style", "width"]);
__publicField(_VictoryLineBase, "displayName", "VictoryLine");
__publicField(_VictoryLineBase, "role", "line");
__publicField(_VictoryLineBase, "defaultTransitions", default_transitions_exports.continuousTransitions());
__publicField(_VictoryLineBase, "defaultPolarTransitions", default_transitions_exports.continuousPolarTransitions());
__publicField(_VictoryLineBase, "continuous", true);
__publicField(_VictoryLineBase, "defaultProps", {
  containerComponent: import_react70.default.createElement(VictoryContainer, null),
  dataComponent: import_react70.default.createElement(Curve, null),
  labelComponent: import_react70.default.createElement(VictoryLabel, {
    renderInPortal: true
  }),
  groupComponent: import_react70.default.createElement(VictoryClipContainer, null),
  samples: 50,
  sortKey: "x",
  sortOrder: "ascending",
  standalone: true,
  theme: VictoryTheme.grayscale
});
__publicField(_VictoryLineBase, "getDomain", domain_exports.getDomain);
__publicField(_VictoryLineBase, "getData", data_exports.getData);
__publicField(_VictoryLineBase, "expectedComponents", ["dataComponent", "labelComponent", "groupComponent", "containerComponent"]);
var VictoryLineBase = _VictoryLineBase;
var VictoryLine = addEvents(VictoryLineBase, options6);

// node_modules/victory-pie/es/victory-pie.js
var import_react72 = __toESM(require_react());

// node_modules/victory-pie/es/helper-methods.js
var import_isPlainObject9 = __toESM(require_isPlainObject());
var import_defaults44 = __toESM(require_defaults());
var checkForValidText = (text) => {
  if (text === void 0 || text === null || helpers_exports.isFunction(text)) {
    return text;
  }
  return `${text}`;
};
var getColor2 = (style, colors3, index) => {
  if (style && style.data && style.data.fill) {
    return style.data.fill;
  }
  return colors3 && colors3[index % colors3.length];
};
var getRadius3 = (props, padding2) => {
  if (typeof props.radius === "number") {
    return props.radius;
  }
  return Math.min(props.width - padding2.left - padding2.right, props.height - padding2.top - padding2.bottom) / 2;
};
var getOrigin2 = (props, padding2) => {
  const {
    width,
    height
  } = props;
  const origin = (0, import_isPlainObject9.default)(props.origin) ? props.origin : {};
  return {
    x: origin.x !== void 0 ? origin.x : (padding2.left - padding2.right + width) / 2,
    y: origin.y !== void 0 ? origin.y : (padding2.top - padding2.bottom + height) / 2
  };
};
var getSlices = (props, data) => {
  const padAngle = helpers_exports.isFunction(props.padAngle) ? 0 : props.padAngle;
  const layoutFunction = pie_default().sort(null).startAngle(helpers_exports.degreesToRadians(props.startAngle)).endAngle(helpers_exports.degreesToRadians(props.endAngle)).padAngle(helpers_exports.degreesToRadians(padAngle)).value((datum) => {
    return datum._y;
  });
  return layoutFunction(data);
};
var getCalculatedValues11 = (props) => {
  const {
    colorScale
  } = props;
  const styleObject = helpers_exports.getDefaultStyles(props, "pie");
  const style = helpers_exports.getStyles(props.style, styleObject);
  const colors3 = Array.isArray(colorScale) ? colorScale : style_exports.getColorScale(colorScale);
  const padding2 = helpers_exports.getPadding(props);
  const defaultRadius = getRadius3(props, padding2);
  const origin = getOrigin2(props, padding2);
  const data = data_exports.getData(props);
  const slices = getSlices(props, data);
  return Object.assign({}, props, {
    style,
    colors: colors3,
    padding: padding2,
    defaultRadius,
    data,
    slices,
    origin
  });
};
var getSliceStyle = (index, calculatedValues) => {
  const {
    style,
    colors: colors3
  } = calculatedValues;
  const fill = getColor2(style, colors3, index);
  return Object.assign({
    fill
  }, style.data);
};
var getLabelText = (props, datum, index) => {
  let text;
  if (datum.label) {
    text = datum.label;
  } else if (Array.isArray(props.labels)) {
    text = props.labels[index];
  } else {
    text = helpers_exports.isFunction(props.labels) ? props.labels : datum.xName || datum._x;
  }
  return checkForValidText(text);
};
var getLabelArc = (labelRadius) => {
  return arc_default().outerRadius(labelRadius).innerRadius(labelRadius);
};
var getCalculatedLabelRadius = (radius, labelRadius, style) => {
  const padding2 = style && style.padding || 0;
  return labelRadius || radius + padding2;
};
var getLabelPosition = (arc, slice, position) => {
  const construct = {
    startAngle: position === "startAngle" ? slice.startAngle : slice.endAngle,
    endAngle: position === "endAngle" ? slice.endAngle : slice.startAngle
  };
  const clonedArc = Object.assign({}, slice, construct);
  return arc.centroid(clonedArc);
};
var getLabelOrientation = (degree, labelPlacement) => {
  if (labelPlacement === "perpendicular") {
    return degree > 90 && degree < 270 ? "bottom" : "top";
  } else if (labelPlacement === "parallel") {
    return degree >= 0 && degree <= 180 ? "right" : "left";
  }
  if (degree < 45 || degree > 315) {
    return "top";
  } else if (degree >= 45 && degree < 135) {
    return "right";
  } else if (degree >= 135 && degree < 225) {
    return "bottom";
  }
  return "left";
};
var getTextAnchor2 = (orientation) => {
  if (orientation === "top" || orientation === "bottom") {
    return "middle";
  }
  return orientation === "right" ? "start" : "end";
};
var getVerticalAnchor2 = (orientation) => {
  if (orientation === "left" || orientation === "right") {
    return "middle";
  }
  return orientation === "bottom" ? "start" : "end";
};
var getBaseLabelAngle = (slice, labelPosition, labelStyle) => {
  let baseAngle = 0;
  if (labelPosition.angle !== void 0) {
    baseAngle = labelStyle.angle;
  } else if (labelPosition === "centroid") {
    baseAngle = helpers_exports.radiansToDegrees((slice.startAngle + slice.endAngle) / 2);
  } else {
    baseAngle = labelPosition === "startAngle" ? helpers_exports.radiansToDegrees(slice.startAngle) : helpers_exports.radiansToDegrees(slice.endAngle);
  }
  const positiveAngle = baseAngle < 0 ? 360 - baseAngle : baseAngle;
  return positiveAngle % 360;
};
var getLabelAngle = (baseAngle, labelPlacement) => {
  if (labelPlacement === "vertical") {
    return 0;
  }
  if (labelPlacement === "parallel") {
    return baseAngle > 180 && baseAngle < 360 ? baseAngle + 90 : baseAngle - 90;
  }
  return baseAngle > 90 && baseAngle < 270 ? baseAngle - 180 : baseAngle;
};
var getLabelProps4 = (text, dataProps, calculatedValues) => {
  const {
    index,
    datum,
    data,
    slice,
    labelComponent,
    theme
  } = dataProps;
  const {
    style,
    defaultRadius,
    origin,
    width,
    height
  } = calculatedValues;
  const labelRadius = helpers_exports.evaluateProp(calculatedValues.labelRadius, Object.assign({
    text
  }, dataProps));
  const labelPosition = helpers_exports.evaluateProp(calculatedValues.labelPosition, Object.assign({
    text
  }, dataProps)) || "centroid";
  const labelPlacement = helpers_exports.evaluateProp(calculatedValues.labelPlacement, Object.assign({
    text
  }, dataProps)) || "vertical";
  const labelStyle = Object.assign({
    padding: 0
  }, style.labels);
  const evaluatedStyle = helpers_exports.evaluateStyle(labelStyle, Object.assign({
    labelRadius,
    text
  }, dataProps));
  const calculatedLabelRadius = getCalculatedLabelRadius(defaultRadius, labelRadius, evaluatedStyle);
  const labelArc = getLabelArc(calculatedLabelRadius);
  const position = getLabelPosition(labelArc, slice, labelPosition);
  const baseAngle = getBaseLabelAngle(slice, labelPosition, labelStyle);
  const labelAngle = getLabelAngle(baseAngle, labelPlacement);
  const orientation = getLabelOrientation(baseAngle, labelPlacement);
  const textAnchor = labelStyle.textAnchor || getTextAnchor2(orientation);
  const verticalAnchor = labelStyle.verticalAnchor || getVerticalAnchor2(orientation);
  const labelProps = {
    width,
    height,
    index,
    datum,
    data,
    slice,
    orientation,
    text,
    style: labelStyle,
    x: Math.round(position[0]) + origin.x,
    y: Math.round(position[1]) + origin.y,
    textAnchor,
    verticalAnchor,
    angle: labelAngle,
    calculatedLabelRadius
  };
  if (!helpers_exports.isTooltip(labelComponent)) {
    return labelProps;
  }
  const tooltipTheme = theme && theme.tooltip || {};
  return (0, import_defaults44.default)({}, labelProps, helpers_exports.omit(tooltipTheme, ["style"]));
};
var getXOffsetMultiplayerByAngle = (angle) => Math.cos(angle - helpers_exports.degreesToRadians(90));
var getYOffsetMultiplayerByAngle = (angle) => Math.sin(angle - helpers_exports.degreesToRadians(90));
var getXOffset = (offset, angle) => offset * getXOffsetMultiplayerByAngle(angle);
var getYOffset = (offset, angle) => offset * getYOffsetMultiplayerByAngle(angle);
var getAverage = (array) => array.reduce((acc, cur) => acc + cur, 0) / array.length;
var getLabelIndicatorPropsForLineSegment = (props, calculatedValues, labelProps) => {
  const {
    innerRadius,
    radius,
    slice: {
      startAngle,
      endAngle
    },
    labelIndicatorInnerOffset,
    labelIndicatorOuterOffset,
    index
  } = props;
  const {
    height,
    width
  } = calculatedValues;
  const {
    calculatedLabelRadius
  } = labelProps;
  const middleRadius = getAverage([innerRadius, radius]);
  const midAngle = getAverage([endAngle, startAngle]);
  const centerX = width / 2;
  const centerY = height / 2;
  const innerOffset = middleRadius + labelIndicatorInnerOffset;
  const outerOffset = calculatedLabelRadius - labelIndicatorOuterOffset;
  const x1 = centerX + getXOffset(innerOffset, midAngle);
  const y1 = centerY + getYOffset(innerOffset, midAngle);
  const x2 = centerX + getXOffset(outerOffset, midAngle);
  const y2 = centerY + getYOffset(outerOffset, midAngle);
  const labelIndicatorProps = {
    x1,
    y1,
    x2,
    y2,
    index
  };
  return (0, import_defaults44.default)({}, labelIndicatorProps);
};
var getBaseProps11 = (initialProps, fallbackProps22) => {
  const props = helpers_exports.modifyProps(initialProps, fallbackProps22, "pie");
  const calculatedValues = getCalculatedValues11(props);
  const {
    slices,
    style,
    data,
    origin,
    defaultRadius,
    labels,
    events,
    sharedEvents,
    height,
    width,
    standalone,
    name,
    innerRadius,
    cornerRadius,
    padAngle,
    disableInlineStyles,
    labelIndicator
  } = calculatedValues;
  const radius = props.radius || defaultRadius;
  const initialChildProps = {
    parent: {
      standalone,
      height,
      width,
      slices,
      name,
      style: style.parent
    }
  };
  return slices.reduce((childProps, slice, index) => {
    const datum = (0, import_defaults44.default)({}, data[index], {
      startAngle: helpers_exports.radiansToDegrees(slice.startAngle),
      endAngle: helpers_exports.radiansToDegrees(slice.endAngle),
      padAngle: helpers_exports.radiansToDegrees(slice.padAngle)
    });
    const eventKey = !helpers_exports.isNil(datum.eventKey) ? datum.eventKey : index;
    const dataProps = {
      index,
      slice,
      datum,
      data,
      origin,
      innerRadius,
      radius,
      cornerRadius,
      padAngle,
      style: disableInlineStyles ? {} : getSliceStyle(index, calculatedValues),
      disableInlineStyles
    };
    childProps[eventKey] = {
      data: dataProps
    };
    const text = getLabelText(props, datum, index);
    if (text !== void 0 && text !== null || labels && (events || sharedEvents)) {
      const evaluatedText = helpers_exports.evaluateProp(text, dataProps);
      childProps[eventKey].labels = getLabelProps4(evaluatedText, Object.assign({}, props, dataProps), calculatedValues);
      if (labelIndicator) {
        const labelProps = childProps[eventKey].labels;
        if (labelProps.calculatedLabelRadius > radius) {
          childProps[eventKey].labelIndicators = getLabelIndicatorPropsForLineSegment(Object.assign({}, props, dataProps), calculatedValues, labelProps);
        }
      }
    }
    return childProps;
  }, initialChildProps);
};

// node_modules/victory-pie/es/slice.js
var import_defaults45 = __toESM(require_defaults());
var import_react71 = __toESM(require_react());
var getPath3 = (props) => {
  const {
    slice,
    radius,
    innerRadius,
    cornerRadius
  } = props;
  if (helpers_exports.isFunction(props.pathFunction)) {
    return props.pathFunction(slice);
  }
  const padAngle = helpers_exports.degreesToRadians(props.padAngle);
  const startAngle = helpers_exports.degreesToRadians(props.sliceStartAngle);
  const endAngle = helpers_exports.degreesToRadians(props.sliceEndAngle);
  const pathFunction = arc_default().cornerRadius(cornerRadius).outerRadius(radius).innerRadius(innerRadius || 0);
  return pathFunction((0, import_defaults45.default)({
    startAngle,
    endAngle,
    padAngle
  }, slice));
};
var evaluateProps16 = (props) => {
  const style = helpers_exports.evaluateStyle(props.style, props);
  const radius = helpers_exports.evaluateProp(props.radius, Object.assign({}, props, {
    style
  }));
  const innerRadius = helpers_exports.evaluateProp(props.innerRadius, Object.assign({}, props, {
    style,
    radius
  }));
  const ariaLabel = helpers_exports.evaluateProp(props.ariaLabel, props);
  const id = helpers_exports.evaluateProp(props.id, props);
  const cornerRadius = helpers_exports.evaluateProp(props.cornerRadius, props);
  const padAngle = helpers_exports.evaluateProp(props.padAngle, props);
  const sliceStartAngle = helpers_exports.evaluateProp(props.sliceStartAngle, props);
  const sliceEndAngle = helpers_exports.evaluateProp(props.sliceEndAngle, props);
  const tabIndex = helpers_exports.evaluateProp(props.tabIndex, props);
  return Object.assign({}, props, {
    ariaLabel,
    style,
    radius,
    innerRadius,
    id,
    cornerRadius,
    padAngle,
    sliceStartAngle,
    sliceEndAngle,
    tabIndex
  });
};
var defaultProps18 = {
  pathComponent: import_react71.default.createElement(Path, null),
  role: "presentation",
  shapeRendering: "auto"
};
var Slice = (initialProps) => {
  const props = evaluateProps16((0, import_defaults45.default)({}, initialProps, defaultProps18));
  const defaultTransform = props.origin ? `translate(${props.origin.x}, ${props.origin.y})` : void 0;
  return import_react71.default.cloneElement(props.pathComponent, {
    ...props.events,
    "aria-label": props.ariaLabel,
    d: getPath3(props),
    style: props.style,
    transform: props.transform || defaultTransform,
    className: props.className,
    role: props.role,
    shapeRendering: props.shapeRendering,
    clipPath: props.clipPath,
    tabIndex: props.tabIndex
  });
};

// node_modules/victory-pie/es/victory-pie.js
var fallbackProps17 = {
  endAngle: 360,
  height: 400,
  innerRadius: 0,
  cornerRadius: 0,
  padAngle: 0,
  padding: 30,
  width: 400,
  startAngle: 0,
  colorScale: ["#ffffff", "#f0f0f0", "#d9d9d9", "#bdbdbd", "#969696", "#737373", "#525252", "#252525", "#000000"],
  labelPosition: "centroid",
  labelIndicatorInnerOffset: 15,
  labelIndicatorOuterOffset: 5
};
var datumHasXandY3 = (datum) => {
  return !helpers_exports.isNil(datum._x) && !helpers_exports.isNil(datum._y);
};
var VictoryPieBase = class extends import_react72.default.Component {
  static getBaseProps(props) {
    return getBaseProps11(props, fallbackProps17);
  }
  // Overridden in victory-native
  shouldAnimate() {
    return Boolean(this.props.animate);
  }
  renderComponents(props, shouldRenderDatum) {
    if (shouldRenderDatum === void 0) {
      shouldRenderDatum = datumHasXandY3;
    }
    const {
      dataComponent,
      labelComponent,
      groupComponent,
      labelIndicator,
      labelPosition
    } = props;
    if (!groupComponent) {
      throw new Error("VictoryPie expects a groupComponent prop");
    }
    const showIndicator = labelIndicator && labelPosition === "centroid";
    const children = [];
    if (dataComponent) {
      const dataComponents = this.dataKeys.reduce((validDataComponents, _dataKey, index) => {
        const dataProps = this.getComponentProps(dataComponent, "data", index);
        if (shouldRenderDatum(dataProps.datum)) {
          validDataComponents.push(import_react72.default.cloneElement(dataComponent, dataProps));
        }
        return validDataComponents;
      }, []);
      children.push(...dataComponents);
    }
    if (labelComponent) {
      const labelComponents = this.dataKeys.map((_dataKey, index) => {
        const labelProps = this.getComponentProps(labelComponent, "labels", index);
        if (labelProps.text !== void 0 && labelProps.text !== null) {
          return import_react72.default.cloneElement(labelComponent, labelProps);
        }
        return void 0;
      }).filter((comp) => comp !== void 0);
      children.push(...labelComponents);
    }
    if (showIndicator && labelIndicator) {
      let labelIndicatorComponent = import_react72.default.createElement(LineSegment, null);
      if (typeof labelIndicator === "object") {
        labelIndicatorComponent = labelIndicator;
      }
      const labelIndicatorComponents = this.dataKeys.map((_dataKey, index) => {
        const labelIndicatorProps = this.getComponentProps(labelIndicatorComponent, "labelIndicators", index);
        return import_react72.default.cloneElement(labelIndicatorComponent, labelIndicatorProps);
      });
      children.push(...labelIndicatorComponents);
    }
    return this.renderContainer(groupComponent, children);
  }
  render() {
    const {
      animationWhitelist,
      role
    } = VictoryPie;
    const props = helpers_exports.modifyProps(this.props, fallbackProps17, role);
    if (this.shouldAnimate()) {
      return this.animateComponent(props, animationWhitelist);
    }
    const children = this.renderComponents(props);
    const component = props.standalone ? this.renderContainer(props.containerComponent, children) : children;
    return user_props_exports.withSafeUserProps(component, props);
  }
};
__publicField(VictoryPieBase, "animationWhitelist", ["data", "endAngle", "height", "innerRadius", "cornerRadius", "padAngle", "padding", "colorScale", "startAngle", "style", "width"]);
__publicField(VictoryPieBase, "displayName", "VictoryPie");
__publicField(VictoryPieBase, "role", "pie");
__publicField(VictoryPieBase, "defaultTransitions", {
  onExit: {
    duration: 500,
    before: () => ({
      _y: 0,
      label: " "
    })
  },
  onEnter: {
    duration: 500,
    before: () => ({
      _y: 0,
      label: " "
    }),
    after: (datum) => ({
      y_: datum._y,
      label: datum.label
    })
  }
});
__publicField(VictoryPieBase, "defaultProps", {
  data: [{
    x: "A",
    y: 1
  }, {
    x: "B",
    y: 2
  }, {
    x: "C",
    y: 3
  }, {
    x: "D",
    y: 1
  }, {
    x: "E",
    y: 2
  }],
  standalone: true,
  dataComponent: import_react72.default.createElement(Slice, null),
  labelComponent: import_react72.default.createElement(VictoryLabel, null),
  containerComponent: import_react72.default.createElement(VictoryContainer, null),
  groupComponent: import_react72.default.createElement("g", null),
  sortOrder: "ascending",
  theme: VictoryTheme.grayscale
});
__publicField(VictoryPieBase, "getData", data_exports.getData);
__publicField(VictoryPieBase, "expectedComponents", ["dataComponent", "labelComponent", "groupComponent", "containerComponent", "labelIndicatorComponent"]);
var VictoryPie = addEvents(VictoryPieBase);

// node_modules/victory-scatter/es/victory-scatter.js
var import_react73 = __toESM(require_react());

// node_modules/victory-scatter/es/helper-methods.js
var getSymbol = (data, props) => {
  if (props.bubbleProperty) {
    return "circle";
  }
  return data.symbol || props.symbol;
};
var getBubbleSize = (datum, props) => {
  const {
    data,
    z,
    maxBubbleSize,
    minBubbleSize
  } = props;
  const zData = data.map((point3) => point3[z]);
  const zMin = Math.min(...zData);
  const zMax = Math.max(...zData);
  const getMaxRadius = () => {
    const minPadding = Math.min(...Object.values(helpers_exports.getPadding(props)));
    return Math.max(minPadding, 5);
  };
  const maxRadius = maxBubbleSize || getMaxRadius();
  const minRadius = minBubbleSize || maxRadius * 0.1;
  if (zMax === zMin) {
    return Math.max(minRadius, 1);
  }
  const maxArea = Math.PI * Math.pow(maxRadius, 2);
  const minArea = Math.PI * Math.pow(minRadius, 2);
  const pointArea = (datum[z] - zMin) / (zMax - zMin) * maxArea;
  const area = Math.max(pointArea, minArea);
  const radius = Math.sqrt(area / Math.PI);
  return Math.max(radius, 1);
};
var getSize = (datum, props) => {
  const {
    size,
    z
  } = props;
  if (datum.size) {
    return typeof datum.size === "function" ? datum.size : Math.max(datum.size, 1);
  } else if (typeof props.size === "function") {
    return size;
  } else if (datum[z]) {
    return getBubbleSize(datum, props);
  }
  return Math.max(size || 0, 1);
};
var getCalculatedValues12 = (props) => {
  const defaultStyles2 = helpers_exports.getDefaultStyles(props, "scatter");
  const style = helpers_exports.getStyles(props.style, defaultStyles2);
  const range3 = {
    x: helpers_exports.getRange(props, "x"),
    y: helpers_exports.getRange(props, "y")
  };
  const domain = {
    x: domain_exports.getDomain(props, "x"),
    y: domain_exports.getDomain(props, "y")
  };
  const scale = {
    x: scale_exports.getBaseScale(props, "x").domain(domain.x).range(props.horizontal ? range3.y : range3.x),
    y: scale_exports.getBaseScale(props, "y").domain(domain.y).range(props.horizontal ? range3.x : range3.y)
  };
  const origin = props.polar ? props.origin || helpers_exports.getPolarOrigin(props) : void 0;
  const z = props.bubbleProperty || "z";
  let data = data_exports.getData(props);
  data = data_exports.formatDataFromDomain(data, domain);
  return {
    domain,
    data,
    scale,
    style,
    origin,
    z
  };
};
var getBaseProps12 = (initialProps, fallbackProps22) => {
  const modifiedProps = helpers_exports.modifyProps(initialProps, fallbackProps22, "scatter");
  const props = Object.assign({}, modifiedProps, getCalculatedValues12(modifiedProps));
  const {
    data,
    domain,
    events,
    height,
    origin,
    padding: padding2,
    polar,
    scale,
    name,
    sharedEvents,
    standalone,
    style,
    theme,
    width,
    labels,
    horizontal,
    disableInlineStyles
  } = props;
  const initialChildProps = {
    parent: {
      style: style.parent,
      scale,
      domain,
      data,
      height,
      width,
      standalone,
      theme,
      origin,
      polar,
      padding: padding2,
      name,
      horizontal
    }
  };
  return data.reduce((childProps, datum, index) => {
    const eventKey = !helpers_exports.isNil(datum.eventKey) ? datum.eventKey : index;
    const {
      x: x2,
      y: y2
    } = helpers_exports.scalePoint(props, datum);
    const dataProps = {
      x: x2,
      y: y2,
      datum,
      data,
      index,
      scale,
      polar,
      origin,
      horizontal,
      size: getSize(datum, props),
      symbol: getSymbol(datum, props),
      style: disableInlineStyles ? {} : style.data,
      disableInlineStyles
    };
    childProps[eventKey] = {
      data: dataProps
    };
    const text = label_helpers_exports.getText(props, datum, index);
    if (text !== void 0 && text !== null || labels && (events || sharedEvents)) {
      childProps[eventKey].labels = label_helpers_exports.getProps(props, index);
    }
    return childProps;
  }, initialChildProps);
};

// node_modules/victory-scatter/es/victory-scatter.js
var fallbackProps18 = {
  width: 450,
  height: 300,
  padding: 50,
  size: 3,
  symbol: "circle"
};
var VictoryScatterBase = class extends import_react73.default.Component {
  static getBaseProps(props) {
    return getBaseProps12(props, fallbackProps18);
  }
  // Overridden in native versions
  shouldAnimate() {
    return !!this.props.animate;
  }
  render() {
    const {
      animationWhitelist,
      role
    } = VictoryScatter;
    const props = helpers_exports.modifyProps(this.props, fallbackProps18, role);
    if (this.shouldAnimate()) {
      return this.animateComponent(props, animationWhitelist);
    }
    const children = this.renderData(props);
    const component = props.standalone ? this.renderContainer(props.containerComponent, children) : children;
    return user_props_exports.withSafeUserProps(component, props);
  }
};
__publicField(VictoryScatterBase, "animationWhitelist", ["data", "domain", "height", "maxBubbleSize", "padding", "samples", "size", "style", "width"]);
__publicField(VictoryScatterBase, "displayName", "VictoryScatter");
__publicField(VictoryScatterBase, "role", "scatter");
__publicField(VictoryScatterBase, "defaultTransitions", default_transitions_exports.discreteTransitions());
__publicField(VictoryScatterBase, "defaultProps", {
  containerComponent: import_react73.default.createElement(VictoryContainer, null),
  dataComponent: import_react73.default.createElement(Point, null),
  labelComponent: import_react73.default.createElement(VictoryLabel, null),
  groupComponent: import_react73.default.createElement("g", null),
  samples: 50,
  sortOrder: "ascending",
  standalone: true,
  theme: VictoryTheme.grayscale
});
__publicField(VictoryScatterBase, "getDomain", domain_exports.getDomain);
__publicField(VictoryScatterBase, "getData", data_exports.getData);
__publicField(VictoryScatterBase, "expectedComponents", ["dataComponent", "labelComponent", "groupComponent", "containerComponent"]);
var VictoryScatter = addEvents(VictoryScatterBase);

// node_modules/victory-stack/es/victory-stack.js
var import_isEmpty12 = __toESM(require_isEmpty());
var import_defaults46 = __toESM(require_defaults());
var import_react75 = __toESM(require_react());

// node_modules/victory-stack/es/helper-methods.js
var import_orderBy6 = __toESM(require_orderBy());
var import_react74 = __toESM(require_react());
var import_react_fast_compare12 = __toESM(require_react_fast_compare());
var fallbackProps19 = {
  width: 450,
  height: 300,
  padding: 50
};
function fillData(props, datasets) {
  const {
    fillInMissingData
  } = props;
  const xMap = datasets.reduce((prev, dataset) => {
    dataset.forEach((datum) => {
      prev[datum._x instanceof Date ? datum._x.getTime() : datum._x] = true;
    });
    return prev;
  }, {});
  const xKeys = Object.keys(xMap).map((k) => Number(k));
  const xArr = (0, import_orderBy6.default)(xKeys);
  return datasets.map((dataset) => {
    let indexOffset = 0;
    const isDate = dataset[0] && dataset[0]._x instanceof Date;
    const filledInData = xArr.map((x2, index) => {
      let parsedX = Number(x2);
      const datum = dataset[index - indexOffset];
      if (datum) {
        const x1 = isDate ? datum._x.getTime() : datum._x;
        if (x1 === parsedX) {
          return datum;
        }
        indexOffset++;
        const y3 = fillInMissingData ? 0 : null;
        parsedX = isDate ? new Date(parsedX) : parsedX;
        return {
          x: parsedX,
          y: y3,
          _x: parsedX,
          _y: y3
        };
      }
      const y2 = fillInMissingData ? 0 : null;
      parsedX = isDate ? new Date(parsedX) : parsedX;
      return {
        x: parsedX,
        y: y2,
        _x: parsedX,
        _y: y2
      };
    });
    return filledInData;
  });
}
function getY0(datum, index, datasets) {
  if (datum.y0) {
    return datum.y0;
  }
  const y2 = datum._y;
  const group = datum._group;
  const firstDatasetBaseline = datasets[0].map((d) => d.y0);
  const previousDatasets = datasets.slice(0, index);
  const previousPoints = previousDatasets.reduce((prev, dataset) => {
    return prev.concat(dataset.filter((previousDatum) => datum._x instanceof Date ? previousDatum._x.getTime() === datum._x.getTime() : previousDatum._x === datum._x).map((previousDatum) => previousDatum._y || 0));
  }, []);
  const y0 = previousPoints.length && previousPoints.reduce((memo, value) => {
    const sameSign = y2 < 0 && value < 0 || y2 >= 0 && value >= 0;
    return sameSign ? Number(value) + memo : memo;
  }, firstDatasetBaseline[group] || 0);
  return previousPoints.some((point3) => point3 instanceof Date) ? new Date(y0) : y0;
}
function addLayoutData(props, datasets, index) {
  const xOffset = props.xOffset || 0;
  return datasets[index].map((datum) => {
    const yOffset = getY0(datum, index, datasets) || 0;
    return Object.assign({}, datum, {
      _y0: !(datum._y instanceof Date) ? yOffset : yOffset ? new Date(yOffset) : datum._y,
      _y1: datum._y === null ? null : datum._y instanceof Date ? new Date(Number(datum._y) + Number(yOffset)) : datum._y + yOffset,
      _x1: datum._x === null ? null : datum._x instanceof Date ? new Date(Number(datum._x) + Number(xOffset)) : datum._x + xOffset
    });
  });
}
function stackData(props, childComponents) {
  const dataFromChildren = wrapper_exports.getDataFromChildren(props, childComponents);
  const filledDatasets = fillData(props, dataFromChildren);
  const filteredNullChild = filledDatasets.map((dataset) => dataset.filter((datum) => datum._x !== null && datum._y !== null));
  return filteredNullChild.map((d, i) => addLayoutData(props, filledDatasets, i));
}
function getCalculatedProps4(initialProps, childComponents) {
  const children = childComponents || import_react74.default.Children.toArray(initialProps.children);
  const role = "stack";
  const props = helpers_exports.modifyProps(initialProps, fallbackProps19, role);
  const style = wrapper_exports.getStyle(props.theme, props.style, role);
  const categories = props.categories || wrapper_exports.getCategories(props, children);
  const datasets = props.datasets || stackData(props, children);
  const clonedChildren = children.map((c, i) => {
    return import_react74.default.cloneElement(c, {
      data: datasets[i]
    });
  });
  const domain = {
    x: wrapper_exports.getDomain(Object.assign({}, props, {
      categories
    }), "x", clonedChildren),
    y: wrapper_exports.getDomain(Object.assign({}, props, {
      categories
    }), "y", clonedChildren)
  };
  const range3 = props.range || {
    x: helpers_exports.getRange(props, "x"),
    y: helpers_exports.getRange(props, "y")
  };
  const baseScale = {
    x: scale_exports.getScaleFromProps(props, "x") || wrapper_exports.getScale(props, "x"),
    y: scale_exports.getScaleFromProps(props, "y") || wrapper_exports.getScale(props, "y")
  };
  const scale = {
    x: baseScale.x.domain(domain.x).range(props.horizontal ? range3.y : range3.x),
    y: baseScale.y.domain(domain.y).range(props.horizontal ? range3.x : range3.y)
  };
  const {
    colorScale,
    horizontal
  } = props;
  return {
    datasets,
    categories,
    range: range3,
    domain,
    horizontal,
    scale,
    style,
    colorScale,
    role
  };
}
var withoutSharedEvents2 = (props) => {
  const {
    children
  } = props;
  const modifiedChildren = import_react74.default.Children.toArray(children).map((_child) => {
    const child = _child;
    return {
      ...child,
      props: helpers_exports.omit(child.props, ["sharedEvents"])
    };
  });
  props.children = modifiedChildren;
  return props;
};
function useMemoizedProps2(initialProps) {
  const modifiedProps = withoutSharedEvents2(initialProps);
  const [props, setProps] = import_react74.default.useState(modifiedProps);
  import_react74.default.useEffect(() => {
    if (!(0, import_react_fast_compare12.default)(modifiedProps, props)) {
      setProps(modifiedProps);
    }
  }, [props, setProps, modifiedProps]);
  return import_react74.default.useMemo(() => {
    return getCalculatedProps4(props, props.children);
  }, [props]);
}
function getLabels2(props, datasets, index) {
  if (!props.labels) {
    return void 0;
  }
  return datasets.length === index + 1 ? props.labels : void 0;
}
function getChildProps3(props, calculatedProps) {
  const {
    categories,
    domain,
    range: range3,
    scale,
    horizontal
  } = calculatedProps;
  return {
    height: props.height,
    width: props.width,
    padding: helpers_exports.getPadding(props),
    standalone: false,
    theme: props.theme,
    categories,
    domain,
    range: range3,
    scale,
    horizontal
  };
}
function getColorScale4(props, child) {
  const role = child.type && child.type.role;
  const colorScaleOptions = child.props.colorScale || props.colorScale;
  if (role !== "group" && role !== "stack") {
    return void 0;
  }
  return props.theme ? colorScaleOptions || props.theme.props.colorScale : colorScaleOptions;
}
function getChildren3(initialProps, childComponents, calculatedProps) {
  const props = helpers_exports.modifyProps(initialProps, fallbackProps19, "stack");
  const children = childComponents || import_react74.default.Children.toArray(props.children);
  const newCalculatedProps = calculatedProps || getCalculatedProps4(props, children);
  const {
    datasets
  } = newCalculatedProps;
  const childProps = getChildProps3(props, newCalculatedProps);
  const parentName = props.name || "stack";
  return children.map((child, index) => {
    const role = child.type && child.type.role;
    const data = datasets[index];
    const style = wrapper_exports.getChildStyle(child, index, newCalculatedProps);
    const labels = props.labels ? getLabels2(props, datasets, index) : child.props.labels;
    const name = child.props.name || `${parentName}-${role}-${index}`;
    return import_react74.default.cloneElement(child, Object.assign({
      key: `${name}-key-${index}`,
      labels,
      name,
      domainPadding: child.props.domainPadding || props.domainPadding,
      theme: props.theme,
      labelComponent: props.labelComponent || child.props.labelComponent,
      style,
      colorScale: getColorScale4(props, child),
      data,
      polar: props.polar
    }, childProps));
  });
}

// node_modules/victory-stack/es/victory-stack.js
var import_react_fast_compare13 = __toESM(require_react_fast_compare());
var fallbackProps20 = {
  width: 450,
  height: 300,
  padding: 50
};
var defaultProps19 = {
  containerComponent: import_react75.default.createElement(VictoryContainer, null),
  groupComponent: import_react75.default.createElement("g", null),
  standalone: true,
  theme: VictoryTheme.grayscale,
  fillInMissingData: true
};
var VictoryStackBase = (initialProps) => {
  const {
    role
  } = VictoryStack;
  const propsWithDefaults = import_react75.default.useMemo(() => (0, import_defaults46.default)({}, initialProps, defaultProps19), [initialProps]);
  const {
    setAnimationState,
    getAnimationProps,
    getProps: getProps2
  } = hooks_exports.useAnimationState();
  const props = getProps2(propsWithDefaults);
  const modifiedProps = helpers_exports.modifyProps(props, fallbackProps20, role);
  const {
    eventKey,
    containerComponent,
    standalone,
    groupComponent,
    externalEventMutations,
    width,
    height,
    theme,
    polar,
    horizontal,
    name
  } = modifiedProps;
  const childComponents = import_react75.default.Children.toArray(modifiedProps.children);
  const calculatedProps = useMemoizedProps2(modifiedProps);
  const {
    domain,
    scale,
    style
  } = calculatedProps;
  const newChildren = import_react75.default.useMemo(() => {
    const children = getChildren3(props, childComponents, calculatedProps);
    const orderedChildren = children.map((child, index) => {
      const childProps = Object.assign({
        animate: getAnimationProps(props, child, index)
      }, child.props);
      return import_react75.default.cloneElement(child, childProps);
    });
    return orderedChildren.reverse();
  }, [props, childComponents, calculatedProps, getAnimationProps]);
  const containerProps = import_react75.default.useMemo(() => {
    if (standalone) {
      return {
        domain,
        scale,
        width,
        height,
        standalone,
        theme,
        style: style.parent,
        horizontal,
        polar,
        name
      };
    }
    return {};
  }, [standalone, domain, scale, width, height, theme, style, horizontal, polar, name]);
  const userProps = import_react75.default.useMemo(() => user_props_exports.getSafeUserProps(propsWithDefaults), [propsWithDefaults]);
  const container = import_react75.default.useMemo(() => {
    if (standalone) {
      const defaultContainerProps = (0, import_defaults46.default)({}, containerComponent.props, containerProps, userProps);
      return import_react75.default.cloneElement(containerComponent, defaultContainerProps);
    }
    return import_react75.default.cloneElement(groupComponent, userProps);
  }, [groupComponent, standalone, containerComponent, containerProps, userProps]);
  const events = import_react75.default.useMemo(() => {
    return wrapper_exports.getAllEvents(props);
  }, [props]);
  const previousProps = hooks_exports.usePreviousProps(propsWithDefaults);
  import_react75.default.useEffect(() => {
    return () => {
      if (propsWithDefaults.animate) {
        setAnimationState(previousProps, propsWithDefaults);
      }
    };
  }, [setAnimationState, previousProps, propsWithDefaults]);
  if (!(0, import_isEmpty12.default)(events)) {
    return import_react75.default.createElement(VictorySharedEvents, {
      container,
      eventKey,
      events,
      externalEventMutations
    }, newChildren);
  }
  return import_react75.default.cloneElement(container, container.props, newChildren);
};
var componentConfig2 = {
  role: "stack",
  expectedComponents: ["groupComponent", "containerComponent", "labelComponent"],
  getChildren: getChildren3
};
var VictoryStack = Object.assign(import_react75.default.memo(VictoryStackBase, import_react_fast_compare13.default), componentConfig2);
VictoryStack.displayName = "VictoryStack";

// node_modules/victory-voronoi/es/victory-voronoi.js
var import_react77 = __toESM(require_react());

// node_modules/victory-voronoi/es/voronoi.js
var import_defaults47 = __toESM(require_defaults());
var import_react76 = __toESM(require_react());
var getVoronoiPath = (props) => {
  var _a;
  const {
    polygon
  } = props;
  return Array.isArray(polygon) && polygon.length ? `M ${(_a = props.polygon) == null ? void 0 : _a.join("L")} Z` : "";
};
function evaluateProps17(props) {
  const ariaLabel = helpers_exports.evaluateProp(props.ariaLabel, props);
  const id = helpers_exports.evaluateProp(props.id, props);
  const size = helpers_exports.evaluateProp(props.size, props);
  const style = helpers_exports.evaluateStyle(props.style, props);
  const tabIndex = helpers_exports.evaluateProp(props.tabIndex, props);
  return Object.assign({}, props, {
    ariaLabel,
    id,
    size,
    style,
    tabIndex
  });
}
var defaultProps20 = {
  pathComponent: import_react76.default.createElement(Path, null),
  circleComponent: import_react76.default.createElement(Circle, null),
  clipPathComponent: import_react76.default.createElement(ClipPath, null),
  groupComponent: import_react76.default.createElement("g", null),
  role: "presentation",
  shapeRendering: "auto"
};
var Voronoi = (initialProps) => {
  const props = evaluateProps17((0, import_defaults47.default)({}, initialProps, defaultProps20));
  const {
    ariaLabel,
    role,
    shapeRendering,
    className,
    events,
    transform,
    style,
    size,
    tabIndex
  } = props;
  const voronoiPath = getVoronoiPath(props);
  const sharedProps = {
    "aria-label": ariaLabel,
    className,
    role,
    shapeRendering,
    style,
    tabIndex,
    transform,
    ...events
  };
  const userProps = user_props_exports.getSafeUserProps(props);
  if (size) {
    const circle3 = import_react76.default.cloneElement(props.circleComponent, {
      ...sharedProps,
      key: `${props.id}-circle-clip`,
      clipPath: `url(#${props.clipId})`,
      cx: props.x,
      cy: props.y,
      r: size
    });
    const voronoiClipPath = import_react76.default.cloneElement(props.clipPathComponent, {
      key: `${props.id}-voronoi-clip`,
      clipId: props.clipId
    }, import_react76.default.cloneElement(props.pathComponent, {
      d: voronoiPath,
      className
    }));
    return import_react76.default.cloneElement(props.groupComponent, {}, [voronoiClipPath, circle3]);
  }
  return import_react76.default.cloneElement(props.pathComponent, {
    ...sharedProps,
    ...userProps,
    d: voronoiPath
  });
};

// node_modules/d3-voronoi/src/constant.js
function constant_default(x2) {
  return function() {
    return x2;
  };
}

// node_modules/d3-voronoi/src/point.js
function x(d) {
  return d[0];
}
function y(d) {
  return d[1];
}

// node_modules/d3-voronoi/src/RedBlackTree.js
function RedBlackTree() {
  this._ = null;
}
function RedBlackNode(node) {
  node.U = // parent node
  node.C = // color - true for red, false for black
  node.L = // left node
  node.R = // right node
  node.P = // previous node
  node.N = null;
}
RedBlackTree.prototype = {
  constructor: RedBlackTree,
  insert: function(after, node) {
    var parent, grandpa, uncle;
    if (after) {
      node.P = after;
      node.N = after.N;
      if (after.N) after.N.P = node;
      after.N = node;
      if (after.R) {
        after = after.R;
        while (after.L) after = after.L;
        after.L = node;
      } else {
        after.R = node;
      }
      parent = after;
    } else if (this._) {
      after = RedBlackFirst(this._);
      node.P = null;
      node.N = after;
      after.P = after.L = node;
      parent = after;
    } else {
      node.P = node.N = null;
      this._ = node;
      parent = null;
    }
    node.L = node.R = null;
    node.U = parent;
    node.C = true;
    after = node;
    while (parent && parent.C) {
      grandpa = parent.U;
      if (parent === grandpa.L) {
        uncle = grandpa.R;
        if (uncle && uncle.C) {
          parent.C = uncle.C = false;
          grandpa.C = true;
          after = grandpa;
        } else {
          if (after === parent.R) {
            RedBlackRotateLeft(this, parent);
            after = parent;
            parent = after.U;
          }
          parent.C = false;
          grandpa.C = true;
          RedBlackRotateRight(this, grandpa);
        }
      } else {
        uncle = grandpa.L;
        if (uncle && uncle.C) {
          parent.C = uncle.C = false;
          grandpa.C = true;
          after = grandpa;
        } else {
          if (after === parent.L) {
            RedBlackRotateRight(this, parent);
            after = parent;
            parent = after.U;
          }
          parent.C = false;
          grandpa.C = true;
          RedBlackRotateLeft(this, grandpa);
        }
      }
      parent = after.U;
    }
    this._.C = false;
  },
  remove: function(node) {
    if (node.N) node.N.P = node.P;
    if (node.P) node.P.N = node.N;
    node.N = node.P = null;
    var parent = node.U, sibling, left = node.L, right = node.R, next, red;
    if (!left) next = right;
    else if (!right) next = left;
    else next = RedBlackFirst(right);
    if (parent) {
      if (parent.L === node) parent.L = next;
      else parent.R = next;
    } else {
      this._ = next;
    }
    if (left && right) {
      red = next.C;
      next.C = node.C;
      next.L = left;
      left.U = next;
      if (next !== right) {
        parent = next.U;
        next.U = node.U;
        node = next.R;
        parent.L = node;
        next.R = right;
        right.U = next;
      } else {
        next.U = parent;
        parent = next;
        node = next.R;
      }
    } else {
      red = node.C;
      node = next;
    }
    if (node) node.U = parent;
    if (red) return;
    if (node && node.C) {
      node.C = false;
      return;
    }
    do {
      if (node === this._) break;
      if (node === parent.L) {
        sibling = parent.R;
        if (sibling.C) {
          sibling.C = false;
          parent.C = true;
          RedBlackRotateLeft(this, parent);
          sibling = parent.R;
        }
        if (sibling.L && sibling.L.C || sibling.R && sibling.R.C) {
          if (!sibling.R || !sibling.R.C) {
            sibling.L.C = false;
            sibling.C = true;
            RedBlackRotateRight(this, sibling);
            sibling = parent.R;
          }
          sibling.C = parent.C;
          parent.C = sibling.R.C = false;
          RedBlackRotateLeft(this, parent);
          node = this._;
          break;
        }
      } else {
        sibling = parent.L;
        if (sibling.C) {
          sibling.C = false;
          parent.C = true;
          RedBlackRotateRight(this, parent);
          sibling = parent.L;
        }
        if (sibling.L && sibling.L.C || sibling.R && sibling.R.C) {
          if (!sibling.L || !sibling.L.C) {
            sibling.R.C = false;
            sibling.C = true;
            RedBlackRotateLeft(this, sibling);
            sibling = parent.L;
          }
          sibling.C = parent.C;
          parent.C = sibling.L.C = false;
          RedBlackRotateRight(this, parent);
          node = this._;
          break;
        }
      }
      sibling.C = true;
      node = parent;
      parent = parent.U;
    } while (!node.C);
    if (node) node.C = false;
  }
};
function RedBlackRotateLeft(tree, node) {
  var p = node, q = node.R, parent = p.U;
  if (parent) {
    if (parent.L === p) parent.L = q;
    else parent.R = q;
  } else {
    tree._ = q;
  }
  q.U = parent;
  p.U = q;
  p.R = q.L;
  if (p.R) p.R.U = p;
  q.L = p;
}
function RedBlackRotateRight(tree, node) {
  var p = node, q = node.L, parent = p.U;
  if (parent) {
    if (parent.L === p) parent.L = q;
    else parent.R = q;
  } else {
    tree._ = q;
  }
  q.U = parent;
  p.U = q;
  p.L = q.R;
  if (p.L) p.L.U = p;
  q.R = p;
}
function RedBlackFirst(node) {
  while (node.L) node = node.L;
  return node;
}
var RedBlackTree_default = RedBlackTree;

// node_modules/d3-voronoi/src/Edge.js
function createEdge(left, right, v0, v1) {
  var edge = [null, null], index = edges.push(edge) - 1;
  edge.left = left;
  edge.right = right;
  if (v0) setEdgeEnd(edge, left, right, v0);
  if (v1) setEdgeEnd(edge, right, left, v1);
  cells[left.index].halfedges.push(index);
  cells[right.index].halfedges.push(index);
  return edge;
}
function createBorderEdge(left, v0, v1) {
  var edge = [v0, v1];
  edge.left = left;
  return edge;
}
function setEdgeEnd(edge, left, right, vertex) {
  if (!edge[0] && !edge[1]) {
    edge[0] = vertex;
    edge.left = left;
    edge.right = right;
  } else if (edge.left === right) {
    edge[1] = vertex;
  } else {
    edge[0] = vertex;
  }
}
function clipEdge(edge, x0, y0, x1, y1) {
  var a = edge[0], b = edge[1], ax = a[0], ay = a[1], bx = b[0], by = b[1], t02 = 0, t12 = 1, dx = bx - ax, dy = by - ay, r;
  r = x0 - ax;
  if (!dx && r > 0) return;
  r /= dx;
  if (dx < 0) {
    if (r < t02) return;
    if (r < t12) t12 = r;
  } else if (dx > 0) {
    if (r > t12) return;
    if (r > t02) t02 = r;
  }
  r = x1 - ax;
  if (!dx && r < 0) return;
  r /= dx;
  if (dx < 0) {
    if (r > t12) return;
    if (r > t02) t02 = r;
  } else if (dx > 0) {
    if (r < t02) return;
    if (r < t12) t12 = r;
  }
  r = y0 - ay;
  if (!dy && r > 0) return;
  r /= dy;
  if (dy < 0) {
    if (r < t02) return;
    if (r < t12) t12 = r;
  } else if (dy > 0) {
    if (r > t12) return;
    if (r > t02) t02 = r;
  }
  r = y1 - ay;
  if (!dy && r < 0) return;
  r /= dy;
  if (dy < 0) {
    if (r > t12) return;
    if (r > t02) t02 = r;
  } else if (dy > 0) {
    if (r < t02) return;
    if (r < t12) t12 = r;
  }
  if (!(t02 > 0) && !(t12 < 1)) return true;
  if (t02 > 0) edge[0] = [ax + t02 * dx, ay + t02 * dy];
  if (t12 < 1) edge[1] = [ax + t12 * dx, ay + t12 * dy];
  return true;
}
function connectEdge(edge, x0, y0, x1, y1) {
  var v1 = edge[1];
  if (v1) return true;
  var v0 = edge[0], left = edge.left, right = edge.right, lx = left[0], ly = left[1], rx = right[0], ry = right[1], fx = (lx + rx) / 2, fy = (ly + ry) / 2, fm, fb;
  if (ry === ly) {
    if (fx < x0 || fx >= x1) return;
    if (lx > rx) {
      if (!v0) v0 = [fx, y0];
      else if (v0[1] >= y1) return;
      v1 = [fx, y1];
    } else {
      if (!v0) v0 = [fx, y1];
      else if (v0[1] < y0) return;
      v1 = [fx, y0];
    }
  } else {
    fm = (lx - rx) / (ry - ly);
    fb = fy - fm * fx;
    if (fm < -1 || fm > 1) {
      if (lx > rx) {
        if (!v0) v0 = [(y0 - fb) / fm, y0];
        else if (v0[1] >= y1) return;
        v1 = [(y1 - fb) / fm, y1];
      } else {
        if (!v0) v0 = [(y1 - fb) / fm, y1];
        else if (v0[1] < y0) return;
        v1 = [(y0 - fb) / fm, y0];
      }
    } else {
      if (ly < ry) {
        if (!v0) v0 = [x0, fm * x0 + fb];
        else if (v0[0] >= x1) return;
        v1 = [x1, fm * x1 + fb];
      } else {
        if (!v0) v0 = [x1, fm * x1 + fb];
        else if (v0[0] < x0) return;
        v1 = [x0, fm * x0 + fb];
      }
    }
  }
  edge[0] = v0;
  edge[1] = v1;
  return true;
}
function clipEdges(x0, y0, x1, y1) {
  var i = edges.length, edge;
  while (i--) {
    if (!connectEdge(edge = edges[i], x0, y0, x1, y1) || !clipEdge(edge, x0, y0, x1, y1) || !(Math.abs(edge[0][0] - edge[1][0]) > epsilon || Math.abs(edge[0][1] - edge[1][1]) > epsilon)) {
      delete edges[i];
    }
  }
}

// node_modules/d3-voronoi/src/Cell.js
function createCell(site) {
  return cells[site.index] = {
    site,
    halfedges: []
  };
}
function cellHalfedgeAngle(cell, edge) {
  var site = cell.site, va = edge.left, vb = edge.right;
  if (site === vb) vb = va, va = site;
  if (vb) return Math.atan2(vb[1] - va[1], vb[0] - va[0]);
  if (site === va) va = edge[1], vb = edge[0];
  else va = edge[0], vb = edge[1];
  return Math.atan2(va[0] - vb[0], vb[1] - va[1]);
}
function cellHalfedgeStart(cell, edge) {
  return edge[+(edge.left !== cell.site)];
}
function cellHalfedgeEnd(cell, edge) {
  return edge[+(edge.left === cell.site)];
}
function sortCellHalfedges() {
  for (var i = 0, n = cells.length, cell, halfedges, j, m; i < n; ++i) {
    if ((cell = cells[i]) && (m = (halfedges = cell.halfedges).length)) {
      var index = new Array(m), array = new Array(m);
      for (j = 0; j < m; ++j) index[j] = j, array[j] = cellHalfedgeAngle(cell, edges[halfedges[j]]);
      index.sort(function(i2, j2) {
        return array[j2] - array[i2];
      });
      for (j = 0; j < m; ++j) array[j] = halfedges[index[j]];
      for (j = 0; j < m; ++j) halfedges[j] = array[j];
    }
  }
}
function clipCells(x0, y0, x1, y1) {
  var nCells = cells.length, iCell, cell, site, iHalfedge, halfedges, nHalfedges, start, startX, startY, end, endX, endY, cover = true;
  for (iCell = 0; iCell < nCells; ++iCell) {
    if (cell = cells[iCell]) {
      site = cell.site;
      halfedges = cell.halfedges;
      iHalfedge = halfedges.length;
      while (iHalfedge--) {
        if (!edges[halfedges[iHalfedge]]) {
          halfedges.splice(iHalfedge, 1);
        }
      }
      iHalfedge = 0, nHalfedges = halfedges.length;
      while (iHalfedge < nHalfedges) {
        end = cellHalfedgeEnd(cell, edges[halfedges[iHalfedge]]), endX = end[0], endY = end[1];
        start = cellHalfedgeStart(cell, edges[halfedges[++iHalfedge % nHalfedges]]), startX = start[0], startY = start[1];
        if (Math.abs(endX - startX) > epsilon || Math.abs(endY - startY) > epsilon) {
          halfedges.splice(iHalfedge, 0, edges.push(createBorderEdge(
            site,
            end,
            Math.abs(endX - x0) < epsilon && y1 - endY > epsilon ? [x0, Math.abs(startX - x0) < epsilon ? startY : y1] : Math.abs(endY - y1) < epsilon && x1 - endX > epsilon ? [Math.abs(startY - y1) < epsilon ? startX : x1, y1] : Math.abs(endX - x1) < epsilon && endY - y0 > epsilon ? [x1, Math.abs(startX - x1) < epsilon ? startY : y0] : Math.abs(endY - y0) < epsilon && endX - x0 > epsilon ? [Math.abs(startY - y0) < epsilon ? startX : x0, y0] : null
          )) - 1);
          ++nHalfedges;
        }
      }
      if (nHalfedges) cover = false;
    }
  }
  if (cover) {
    var dx, dy, d2, dc = Infinity;
    for (iCell = 0, cover = null; iCell < nCells; ++iCell) {
      if (cell = cells[iCell]) {
        site = cell.site;
        dx = site[0] - x0;
        dy = site[1] - y0;
        d2 = dx * dx + dy * dy;
        if (d2 < dc) dc = d2, cover = cell;
      }
    }
    if (cover) {
      var v00 = [x0, y0], v01 = [x0, y1], v11 = [x1, y1], v10 = [x1, y0];
      cover.halfedges.push(
        edges.push(createBorderEdge(site = cover.site, v00, v01)) - 1,
        edges.push(createBorderEdge(site, v01, v11)) - 1,
        edges.push(createBorderEdge(site, v11, v10)) - 1,
        edges.push(createBorderEdge(site, v10, v00)) - 1
      );
    }
  }
  for (iCell = 0; iCell < nCells; ++iCell) {
    if (cell = cells[iCell]) {
      if (!cell.halfedges.length) {
        delete cells[iCell];
      }
    }
  }
}

// node_modules/d3-voronoi/src/Circle.js
var circlePool = [];
var firstCircle;
function Circle2() {
  RedBlackNode(this);
  this.x = this.y = this.arc = this.site = this.cy = null;
}
function attachCircle(arc) {
  var lArc = arc.P, rArc = arc.N;
  if (!lArc || !rArc) return;
  var lSite = lArc.site, cSite = arc.site, rSite = rArc.site;
  if (lSite === rSite) return;
  var bx = cSite[0], by = cSite[1], ax = lSite[0] - bx, ay = lSite[1] - by, cx = rSite[0] - bx, cy = rSite[1] - by;
  var d = 2 * (ax * cy - ay * cx);
  if (d >= -epsilon2) return;
  var ha = ax * ax + ay * ay, hc = cx * cx + cy * cy, x2 = (cy * ha - ay * hc) / d, y2 = (ax * hc - cx * ha) / d;
  var circle3 = circlePool.pop() || new Circle2();
  circle3.arc = arc;
  circle3.site = cSite;
  circle3.x = x2 + bx;
  circle3.y = (circle3.cy = y2 + by) + Math.sqrt(x2 * x2 + y2 * y2);
  arc.circle = circle3;
  var before = null, node = circles._;
  while (node) {
    if (circle3.y < node.y || circle3.y === node.y && circle3.x <= node.x) {
      if (node.L) node = node.L;
      else {
        before = node.P;
        break;
      }
    } else {
      if (node.R) node = node.R;
      else {
        before = node;
        break;
      }
    }
  }
  circles.insert(before, circle3);
  if (!before) firstCircle = circle3;
}
function detachCircle(arc) {
  var circle3 = arc.circle;
  if (circle3) {
    if (!circle3.P) firstCircle = circle3.N;
    circles.remove(circle3);
    circlePool.push(circle3);
    RedBlackNode(circle3);
    arc.circle = null;
  }
}

// node_modules/d3-voronoi/src/Beach.js
var beachPool = [];
function Beach() {
  RedBlackNode(this);
  this.edge = this.site = this.circle = null;
}
function createBeach(site) {
  var beach = beachPool.pop() || new Beach();
  beach.site = site;
  return beach;
}
function detachBeach(beach) {
  detachCircle(beach);
  beaches.remove(beach);
  beachPool.push(beach);
  RedBlackNode(beach);
}
function removeBeach(beach) {
  var circle3 = beach.circle, x2 = circle3.x, y2 = circle3.cy, vertex = [x2, y2], previous = beach.P, next = beach.N, disappearing = [beach];
  detachBeach(beach);
  var lArc = previous;
  while (lArc.circle && Math.abs(x2 - lArc.circle.x) < epsilon && Math.abs(y2 - lArc.circle.cy) < epsilon) {
    previous = lArc.P;
    disappearing.unshift(lArc);
    detachBeach(lArc);
    lArc = previous;
  }
  disappearing.unshift(lArc);
  detachCircle(lArc);
  var rArc = next;
  while (rArc.circle && Math.abs(x2 - rArc.circle.x) < epsilon && Math.abs(y2 - rArc.circle.cy) < epsilon) {
    next = rArc.N;
    disappearing.push(rArc);
    detachBeach(rArc);
    rArc = next;
  }
  disappearing.push(rArc);
  detachCircle(rArc);
  var nArcs = disappearing.length, iArc;
  for (iArc = 1; iArc < nArcs; ++iArc) {
    rArc = disappearing[iArc];
    lArc = disappearing[iArc - 1];
    setEdgeEnd(rArc.edge, lArc.site, rArc.site, vertex);
  }
  lArc = disappearing[0];
  rArc = disappearing[nArcs - 1];
  rArc.edge = createEdge(lArc.site, rArc.site, null, vertex);
  attachCircle(lArc);
  attachCircle(rArc);
}
function addBeach(site) {
  var x2 = site[0], directrix = site[1], lArc, rArc, dxl, dxr, node = beaches._;
  while (node) {
    dxl = leftBreakPoint(node, directrix) - x2;
    if (dxl > epsilon) node = node.L;
    else {
      dxr = x2 - rightBreakPoint(node, directrix);
      if (dxr > epsilon) {
        if (!node.R) {
          lArc = node;
          break;
        }
        node = node.R;
      } else {
        if (dxl > -epsilon) {
          lArc = node.P;
          rArc = node;
        } else if (dxr > -epsilon) {
          lArc = node;
          rArc = node.N;
        } else {
          lArc = rArc = node;
        }
        break;
      }
    }
  }
  createCell(site);
  var newArc = createBeach(site);
  beaches.insert(lArc, newArc);
  if (!lArc && !rArc) return;
  if (lArc === rArc) {
    detachCircle(lArc);
    rArc = createBeach(lArc.site);
    beaches.insert(newArc, rArc);
    newArc.edge = rArc.edge = createEdge(lArc.site, newArc.site);
    attachCircle(lArc);
    attachCircle(rArc);
    return;
  }
  if (!rArc) {
    newArc.edge = createEdge(lArc.site, newArc.site);
    return;
  }
  detachCircle(lArc);
  detachCircle(rArc);
  var lSite = lArc.site, ax = lSite[0], ay = lSite[1], bx = site[0] - ax, by = site[1] - ay, rSite = rArc.site, cx = rSite[0] - ax, cy = rSite[1] - ay, d = 2 * (bx * cy - by * cx), hb = bx * bx + by * by, hc = cx * cx + cy * cy, vertex = [(cy * hb - by * hc) / d + ax, (bx * hc - cx * hb) / d + ay];
  setEdgeEnd(rArc.edge, lSite, rSite, vertex);
  newArc.edge = createEdge(lSite, site, null, vertex);
  rArc.edge = createEdge(site, rSite, null, vertex);
  attachCircle(lArc);
  attachCircle(rArc);
}
function leftBreakPoint(arc, directrix) {
  var site = arc.site, rfocx = site[0], rfocy = site[1], pby2 = rfocy - directrix;
  if (!pby2) return rfocx;
  var lArc = arc.P;
  if (!lArc) return -Infinity;
  site = lArc.site;
  var lfocx = site[0], lfocy = site[1], plby2 = lfocy - directrix;
  if (!plby2) return lfocx;
  var hl = lfocx - rfocx, aby2 = 1 / pby2 - 1 / plby2, b = hl / plby2;
  if (aby2) return (-b + Math.sqrt(b * b - 2 * aby2 * (hl * hl / (-2 * plby2) - lfocy + plby2 / 2 + rfocy - pby2 / 2))) / aby2 + rfocx;
  return (rfocx + lfocx) / 2;
}
function rightBreakPoint(arc, directrix) {
  var rArc = arc.N;
  if (rArc) return leftBreakPoint(rArc, directrix);
  var site = arc.site;
  return site[1] === directrix ? site[0] : Infinity;
}

// node_modules/d3-voronoi/src/Diagram.js
var epsilon = 1e-6;
var epsilon2 = 1e-12;
var beaches;
var cells;
var circles;
var edges;
function triangleArea(a, b, c) {
  return (a[0] - c[0]) * (b[1] - a[1]) - (a[0] - b[0]) * (c[1] - a[1]);
}
function lexicographic(a, b) {
  return b[1] - a[1] || b[0] - a[0];
}
function Diagram(sites, extent2) {
  var site = sites.sort(lexicographic).pop(), x2, y2, circle3;
  edges = [];
  cells = new Array(sites.length);
  beaches = new RedBlackTree_default();
  circles = new RedBlackTree_default();
  while (true) {
    circle3 = firstCircle;
    if (site && (!circle3 || site[1] < circle3.y || site[1] === circle3.y && site[0] < circle3.x)) {
      if (site[0] !== x2 || site[1] !== y2) {
        addBeach(site);
        x2 = site[0], y2 = site[1];
      }
      site = sites.pop();
    } else if (circle3) {
      removeBeach(circle3.arc);
    } else {
      break;
    }
  }
  sortCellHalfedges();
  if (extent2) {
    var x0 = +extent2[0][0], y0 = +extent2[0][1], x1 = +extent2[1][0], y1 = +extent2[1][1];
    clipEdges(x0, y0, x1, y1);
    clipCells(x0, y0, x1, y1);
  }
  this.edges = edges;
  this.cells = cells;
  beaches = circles = edges = cells = null;
}
Diagram.prototype = {
  constructor: Diagram,
  polygons: function() {
    var edges2 = this.edges;
    return this.cells.map(function(cell) {
      var polygon = cell.halfedges.map(function(i) {
        return cellHalfedgeStart(cell, edges2[i]);
      });
      polygon.data = cell.site.data;
      return polygon;
    });
  },
  triangles: function() {
    var triangles = [], edges2 = this.edges;
    this.cells.forEach(function(cell, i) {
      if (!(m = (halfedges = cell.halfedges).length)) return;
      var site = cell.site, halfedges, j = -1, m, s0, e1 = edges2[halfedges[m - 1]], s1 = e1.left === site ? e1.right : e1.left;
      while (++j < m) {
        s0 = s1;
        e1 = edges2[halfedges[j]];
        s1 = e1.left === site ? e1.right : e1.left;
        if (s0 && s1 && i < s0.index && i < s1.index && triangleArea(site, s0, s1) < 0) {
          triangles.push([site.data, s0.data, s1.data]);
        }
      }
    });
    return triangles;
  },
  links: function() {
    return this.edges.filter(function(edge) {
      return edge.right;
    }).map(function(edge) {
      return {
        source: edge.left.data,
        target: edge.right.data
      };
    });
  },
  find: function(x2, y2, radius) {
    var that = this, i0, i1 = that._found || 0, n = that.cells.length, cell;
    while (!(cell = that.cells[i1])) if (++i1 >= n) return null;
    var dx = x2 - cell.site[0], dy = y2 - cell.site[1], d2 = dx * dx + dy * dy;
    do {
      cell = that.cells[i0 = i1], i1 = null;
      cell.halfedges.forEach(function(e) {
        var edge = that.edges[e], v = edge.left;
        if ((v === cell.site || !v) && !(v = edge.right)) return;
        var vx = x2 - v[0], vy = y2 - v[1], v2 = vx * vx + vy * vy;
        if (v2 < d2) d2 = v2, i1 = v.index;
      });
    } while (i1 !== null);
    that._found = i0;
    return radius == null || d2 <= radius * radius ? cell.site : null;
  }
};

// node_modules/d3-voronoi/src/voronoi.js
function voronoi_default() {
  var x2 = x, y2 = y, extent2 = null;
  function voronoi(data) {
    return new Diagram(data.map(function(d, i) {
      var s = [Math.round(x2(d, i, data) / epsilon) * epsilon, Math.round(y2(d, i, data) / epsilon) * epsilon];
      s.index = i;
      s.data = d;
      return s;
    }), extent2);
  }
  voronoi.polygons = function(data) {
    return voronoi(data).polygons();
  };
  voronoi.links = function(data) {
    return voronoi(data).links();
  };
  voronoi.triangles = function(data) {
    return voronoi(data).triangles();
  };
  voronoi.x = function(_) {
    return arguments.length ? (x2 = typeof _ === "function" ? _ : constant_default(+_), voronoi) : x2;
  };
  voronoi.y = function(_) {
    return arguments.length ? (y2 = typeof _ === "function" ? _ : constant_default(+_), voronoi) : y2;
  };
  voronoi.extent = function(_) {
    return arguments.length ? (extent2 = _ == null ? null : [[+_[0][0], +_[0][1]], [+_[1][0], +_[1][1]]], voronoi) : extent2 && [[extent2[0][0], extent2[0][1]], [extent2[1][0], extent2[1][1]]];
  };
  voronoi.size = function(_) {
    return arguments.length ? (extent2 = _ == null ? null : [[0, 0], [+_[0], +_[1]]], voronoi) : extent2 && [extent2[1][0] - extent2[0][0], extent2[1][1] - extent2[0][1]];
  };
  return voronoi;
}

// node_modules/victory-voronoi/es/helper-methods.js
var getVoronoi = (props, range3, scale) => {
  const minRange = [Math.min(...range3.x), Math.min(...range3.y)];
  const maxRange = [Math.max(...range3.x), Math.max(...range3.y)];
  const angleAccessor = (d) => {
    const x2 = scale.x(d._x1 !== void 0 ? d._x1 : d._x);
    return -1 * x2 + Math.PI / 2;
  };
  const xAccessor = (d) => {
    return props.horizontal ? scale.y(d._y1 !== void 0 ? d._y1 : d._y) : scale.x(d._x1 !== void 0 ? d._x1 : d._x);
  };
  const yAccessor = (d) => {
    return props.horizontal ? scale.x(d._x1 !== void 0 ? d._x1 : d._x) : scale.y(d._y1 !== void 0 ? d._y1 : d._y);
  };
  return voronoi_default().x((d) => props.polar ? angleAccessor(d) : xAccessor(d)).y((d) => yAccessor(d)).extent([minRange, maxRange]);
};
var getCalculatedValues13 = (props) => {
  const defaultStyles2 = props.theme && props.theme.voronoi && props.theme.voronoi.style ? props.theme.voronoi.style : {};
  const style = helpers_exports.getStyles(props.style, defaultStyles2);
  const range3 = {
    x: helpers_exports.getRange(props, "x"),
    y: helpers_exports.getRange(props, "y")
  };
  const domain = {
    x: domain_exports.getDomain(props, "x"),
    y: domain_exports.getDomain(props, "y")
  };
  const scale = {
    x: scale_exports.getBaseScale(props, "x").domain(domain.x).range(props.horizontal ? range3.y : range3.x),
    y: scale_exports.getBaseScale(props, "y").domain(domain.y).range(props.horizontal ? range3.x : range3.y)
  };
  let data = data_exports.getData(props);
  data = data_exports.formatDataFromDomain(data, domain);
  data = data.filter((datum) => {
    if (datum._x === null) {
      return false;
    }
    if (datum._y === null) {
      return false;
    }
    return true;
  });
  const voronoi = getVoronoi(props, range3, scale);
  const polygons = voronoi.polygons(data);
  const origin = props.polar ? props.origin || helpers_exports.getPolarOrigin(props) : void 0;
  return {
    domain,
    data,
    scale,
    style,
    polygons,
    origin
  };
};
var getBaseProps13 = (initialProps, fallbackProps22) => {
  const modifiedProps = helpers_exports.modifyProps(initialProps, fallbackProps22, "scatter");
  const props = Object.assign({}, modifiedProps, getCalculatedValues13(modifiedProps));
  const {
    data,
    domain,
    events,
    height,
    origin,
    padding: padding2,
    polar,
    polygons,
    scale,
    sharedEvents,
    standalone,
    style,
    theme,
    width,
    labels,
    name
  } = props;
  const initialChildProps = {
    parent: {
      style: style.parent,
      scale,
      domain,
      data,
      standalone,
      height,
      width,
      theme,
      origin,
      polar,
      padding: padding2,
      name
    }
  };
  return data.reduce((childProps, datum, index) => {
    var _a;
    const polygon = (_a = polygons[index]) == null ? void 0 : _a.filter((value) => value !== "data");
    const eventKey = !helpers_exports.isNil(datum.eventKey) ? datum.eventKey : index;
    const {
      x: x2,
      y: y2
    } = helpers_exports.scalePoint(props, datum);
    const dataProps = {
      x: x2,
      y: y2,
      datum,
      data,
      index,
      scale,
      polygon,
      origin,
      size: props.size,
      style: style.data
    };
    childProps[eventKey] = {
      data: dataProps
    };
    const text = label_helpers_exports.getText(props, datum, index);
    if (text !== void 0 && text !== null || labels && (events || sharedEvents)) {
      childProps[eventKey].labels = label_helpers_exports.getProps(props, index);
    }
    return childProps;
  }, initialChildProps);
};

// node_modules/victory-voronoi/es/victory-voronoi.js
var fallbackProps21 = {
  width: 450,
  height: 300,
  padding: 50
};
var VictoryVoronoiBase = class extends import_react77.default.Component {
  static getBaseProps(props) {
    return getBaseProps13(props, fallbackProps21);
  }
  // Overridden in native versions
  shouldAnimate() {
    return !!this.props.animate;
  }
  render() {
    const {
      animationWhitelist,
      role
    } = VictoryVoronoi;
    const props = helpers_exports.modifyProps(this.props, fallbackProps21, role);
    if (this.shouldAnimate()) {
      return this.animateComponent(props, animationWhitelist);
    }
    const children = this.renderData(props);
    const component = props.standalone ? this.renderContainer(props.containerComponent, children) : children;
    return user_props_exports.withSafeUserProps(component, props);
  }
};
__publicField(VictoryVoronoiBase, "animationWhitelist", ["data", "domain", "height", "padding", "samples", "size", "style", "width"]);
__publicField(VictoryVoronoiBase, "displayName", "VictoryVoronoi");
__publicField(VictoryVoronoiBase, "role", "voronoi");
__publicField(VictoryVoronoiBase, "defaultTransitions", default_transitions_exports.discreteTransitions());
__publicField(VictoryVoronoiBase, "defaultProps", {
  containerComponent: import_react77.default.createElement(VictoryContainer, null),
  dataComponent: import_react77.default.createElement(Voronoi, null),
  labelComponent: import_react77.default.createElement(VictoryLabel, null),
  groupComponent: import_react77.default.createElement("g", {
    role: "presentation"
  }),
  samples: 50,
  sortOrder: "ascending",
  standalone: true,
  theme: VictoryTheme.grayscale
});
__publicField(VictoryVoronoiBase, "getDomain", domain_exports.getDomain);
__publicField(VictoryVoronoiBase, "getData", data_exports.getData);
__publicField(VictoryVoronoiBase, "expectedComponents", ["dataComponent", "labelComponent", "groupComponent", "containerComponent"]);
var VictoryVoronoi = addEvents(VictoryVoronoiBase);
export {
  Arc,
  Area,
  axis_exports as Axis,
  Background,
  Bar,
  Border,
  Border as Box,
  BrushHelpers,
  Candle,
  CanvasBar,
  CanvasCurve,
  CanvasGroup,
  CanvasPoint,
  Circle,
  ClipPath,
  collection_exports as Collection,
  CursorHelpers,
  Curve,
  data_exports as Data,
  default_transitions_exports as DefaultTransitions,
  domain_exports as Domain,
  ErrorBar,
  events_exports as Events,
  Flyout,
  helpers_exports as Helpers,
  hooks_exports as Hooks,
  immutable_exports as Immutable,
  label_helpers_exports as LabelHelpers,
  Line,
  line_helpers_exports as LineHelpers,
  LineSegment,
  log_exports as Log,
  Path,
  Point,
  point_path_helpers_exports as PointPathHelpers,
  Portal,
  PortalContext,
  PortalOutlet,
  PortalProvider,
  RawZoomHelpers,
  Rect,
  scale_exports as Scale,
  selection_exports as Selection,
  SelectionHelpers,
  Slice,
  style_exports as Style,
  TSpan,
  Text,
  textsize_exports as TextSize,
  Timer,
  timer_context_default as TimerContext,
  transitions_exports as Transitions,
  user_props_exports as UserProps,
  VICTORY_BRUSH_CONTAINER_DEFAULT_PROPS,
  VICTORY_CURSOR_CONTAINER_DEFAULT_PROPS,
  VICTORY_SELECTION_CONTAINER_DEFAULT_PROPS,
  VICTORY_VORONOI_CONTAINER_DEFAULT_PROPS,
  VICTORY_ZOOM_CONTAINER_DEFAULT_PROPS,
  VictoryAccessibleGroup,
  VictoryAnimation,
  VictoryArea,
  VictoryAxis,
  VictoryBar,
  VictoryBoxPlot,
  VictoryBrushContainer,
  VictoryBrushLine,
  VictoryCandlestick,
  VictoryChart,
  VictoryClipContainer,
  VictoryContainer,
  VictoryCursorContainer,
  VictoryErrorBar,
  VictoryGroup,
  VictoryHistogram,
  VictoryLabel,
  VictoryLegend,
  VictoryLine,
  VictoryPie,
  VictoryPolarAxis,
  VictoryPortal,
  VictoryScatter,
  VictorySelectionContainer,
  VictorySharedEvents,
  VictoryStack,
  VictoryTheme,
  VictoryTooltip,
  VictoryTransition,
  VictoryVoronoi,
  VictoryVoronoiContainer,
  VictoryZoomContainer,
  Voronoi,
  VoronoiHelpers,
  Whisker,
  wrapper_exports as Wrapper,
  ZoomHelpers,
  addEvents,
  createContainer,
  getBarPath,
  getBarPosition,
  getBarWidth,
  getCornerRadius,
  getCustomBarPath,
  getHorizontalBarPath,
  getPolarBarPath,
  getStyle2 as getStyle,
  getVerticalBarPath,
  getVerticalPolarBarPath,
  makeCreateContainerFunction,
  mergeRefs,
  useCanvasContext,
  usePortalContext,
  useVictoryBrushContainer,
  useVictoryContainer,
  useVictoryCursorContainer,
  useVictorySelectionContainer,
  useVictoryVoronoiContainer,
  useVictoryZoomContainer
};
//# sourceMappingURL=victory.js.map
