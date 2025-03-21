/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* AttrDef Declarations                                                       *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

#ifdef GET_ATTRDEF_CLASSES
#undef GET_ATTRDEF_CLASSES


namespace mlir {
class AsmParser;
class AsmPrinter;
} // namespace mlir
namespace mlir {
namespace triton {
namespace nvidia_gpu {
class TensorMemorySpaceAttr;
class TensorMemoryEncodingAttr;
class TensorMemoryScalesEncodingAttr;
class TensorMemorySpaceAttr : public ::mlir::Attribute::AttrBase<TensorMemorySpaceAttr, ::mlir::Attribute, ::mlir::AttributeStorage> {
public:
  using Base::Base;
  static constexpr ::llvm::StringLiteral name = "ttng.tensor_memory";
  static constexpr ::llvm::StringLiteral dialectName = "ttng";
  static constexpr ::llvm::StringLiteral getMnemonic() {
    return {"tensor_memory"};
  }

};
namespace detail {
struct TensorMemoryEncodingAttrStorage;
} // namespace detail
class TensorMemoryEncodingAttr : public ::mlir::Attribute::AttrBase<TensorMemoryEncodingAttr, ::mlir::Attribute, detail::TensorMemoryEncodingAttrStorage> {
public:
  using Base::Base;
  static constexpr ::llvm::StringLiteral name = "triton.gpu.tensor_memory_encoding";
  static constexpr ::llvm::StringLiteral dialectName = "ttng";
  static TensorMemoryEncodingAttr get(::mlir::MLIRContext *context, unsigned blockM, unsigned blockN, bool unpacked, unsigned CTASplitM, unsigned CTASplitN);
  static constexpr ::llvm::StringLiteral getMnemonic() {
    return {"tensor_memory_encoding"};
  }

  static ::mlir::Attribute parse(::mlir::AsmParser &odsParser, ::mlir::Type odsType);
  void print(::mlir::AsmPrinter &odsPrinter) const;
  unsigned getBlockM() const;
  unsigned getBlockN() const;
  bool getUnpacked() const;
  unsigned getCTASplitM() const;
  unsigned getCTASplitN() const;
};
namespace detail {
struct TensorMemoryScalesEncodingAttrStorage;
} // namespace detail
class TensorMemoryScalesEncodingAttr : public ::mlir::Attribute::AttrBase<TensorMemoryScalesEncodingAttr, ::mlir::Attribute, detail::TensorMemoryScalesEncodingAttrStorage> {
public:
  using Base::Base;
  static constexpr ::llvm::StringLiteral name = "triton.gpu.tensor_memory_scales_encoding";
  static constexpr ::llvm::StringLiteral dialectName = "ttng";
  static TensorMemoryScalesEncodingAttr get(::mlir::MLIRContext *context, unsigned CTASplitM, unsigned CTASplitN);
  static constexpr ::llvm::StringLiteral getMnemonic() {
    return {"tensor_memory_scales_encoding"};
  }

  static ::mlir::Attribute parse(::mlir::AsmParser &odsParser, ::mlir::Type odsType);
  void print(::mlir::AsmPrinter &odsPrinter) const;
  unsigned getCTASplitM() const;
  unsigned getCTASplitN() const;
};
} // namespace nvidia_gpu
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::nvidia_gpu::TensorMemorySpaceAttr)
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::nvidia_gpu::TensorMemoryEncodingAttr)
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::nvidia_gpu::TensorMemoryScalesEncodingAttr)

#endif  // GET_ATTRDEF_CLASSES

