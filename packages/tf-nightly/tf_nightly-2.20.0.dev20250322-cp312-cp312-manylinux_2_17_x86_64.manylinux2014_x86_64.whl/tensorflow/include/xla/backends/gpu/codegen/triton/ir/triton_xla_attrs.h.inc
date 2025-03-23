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
namespace xla {
class TmaDescriptorAttr;
namespace detail {
struct TmaDescriptorAttrStorage;
} // namespace detail
class TmaDescriptorAttr : public ::mlir::Attribute::AttrBase<TmaDescriptorAttr, ::mlir::Attribute, detail::TmaDescriptorAttrStorage> {
public:
  using Base::Base;
  static constexpr ::llvm::StringLiteral name = "triton_xla.tma_descriptor";
  static constexpr ::llvm::StringLiteral dialectName = "triton_xla";
  static TmaDescriptorAttr get(::mlir::MLIRContext *context, ::llvm::ArrayRef<int64_t> global_shape, ::llvm::ArrayRef<int64_t> block_shape, int element_byte_size);
  static constexpr ::llvm::StringLiteral getMnemonic() {
    return {"tma_descriptor"};
  }

  static ::mlir::Attribute parse(::mlir::AsmParser &odsParser, ::mlir::Type odsType);
  void print(::mlir::AsmPrinter &odsPrinter) const;
  ::llvm::ArrayRef<int64_t> getGlobalShape() const;
  ::llvm::ArrayRef<int64_t> getBlockShape() const;
  int getElementByteSize() const;
};
} // namespace xla
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::xla::TmaDescriptorAttr)

#endif  // GET_ATTRDEF_CLASSES

