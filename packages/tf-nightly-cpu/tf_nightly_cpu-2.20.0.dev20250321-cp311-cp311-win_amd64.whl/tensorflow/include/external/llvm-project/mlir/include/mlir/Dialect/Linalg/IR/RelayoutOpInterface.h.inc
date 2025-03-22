/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Interface Declarations                                                     *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

namespace mlir {
namespace linalg {
class RelayoutOpInterface;
namespace detail {
struct RelayoutOpInterfaceInterfaceTraits {
  struct Concept {
    /// The methods defined by the interface.
  };
  template<typename ConcreteOp>
  class Model : public Concept {
  public:
    using Interface = ::mlir::linalg::RelayoutOpInterface;
    Model() : Concept{} {}

  };
  template<typename ConcreteOp>
  class FallbackModel : public Concept {
  public:
    using Interface = ::mlir::linalg::RelayoutOpInterface;
    FallbackModel() : Concept{} {}

  };
  template<typename ConcreteModel, typename ConcreteOp>
  class ExternalModel : public FallbackModel<ConcreteModel> {
  public:
    using ConcreteEntity = ConcreteOp;
  };
};
template <typename ConcreteOp>
struct RelayoutOpInterfaceTrait;

} // namespace detail
class RelayoutOpInterface : public ::mlir::OpInterface<RelayoutOpInterface, detail::RelayoutOpInterfaceInterfaceTraits> {
public:
  using ::mlir::OpInterface<RelayoutOpInterface, detail::RelayoutOpInterfaceInterfaceTraits>::OpInterface;
  template <typename ConcreteOp>
  struct Trait : public detail::RelayoutOpInterfaceTrait<ConcreteOp> {};
};
namespace detail {
  template <typename ConcreteOp>
  struct RelayoutOpInterfaceTrait : public ::mlir::OpInterface<RelayoutOpInterface, detail::RelayoutOpInterfaceInterfaceTraits>::Trait<ConcreteOp> {
  };
}// namespace detail
} // namespace linalg
} // namespace mlir
namespace mlir {
namespace linalg {
} // namespace linalg
} // namespace mlir
